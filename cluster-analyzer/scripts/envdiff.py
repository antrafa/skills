#!/usr/bin/env python3
"""Compara as variáveis de ambiente de um Deployment entre dois ambientes, só com leitura.

Uso:
  envdiff.py <deployment> --a <kubeconfig> <contexto> <namespace> \
                          --b <kubeconfig> <contexto> <namespace> [--container <nome>]

Lê o Deployment e os ConfigMaps que ele referencia (env e envFrom) nos dois lados e
imprime a imagem de cada container, o que só existe em A, o que só existe em B e o
que difere. Secret nunca é lido: aparece como referência (secret:<nome>/<chave>).
Valor de chave com cara de credencial sai mascarado; o script diz só se é igual ou
diferente. Se um ConfigMap não puder ser lido (403, inexistente), a variável aparece
como ilegível e o resto segue.
"""
import argparse
import json
import re
import subprocess
import sys

CREDENCIAL = re.compile(r"pass|pwd|secret|token|credential|private|apikey|api_key", re.I)


def kubectl(lado, *args):
    kubeconfig, contexto, namespace = lado
    cmd = ["kubectl", "--kubeconfig", kubeconfig, "--context", contexto, "-n", namespace, *args, "-o", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else f"exit {r.returncode}")
    return json.loads(r.stdout)


def ler_configmap(lado, nome, cache):
    if nome not in cache:
        try:
            cache[nome] = kubectl(lado, "get", "configmap", nome).get("data") or {}
        except RuntimeError as e:
            cache[nome] = e
    return cache[nome]


def valor_do_configmap(lado, nome, chave, cache):
    data = ler_configmap(lado, nome, cache)
    if isinstance(data, Exception):
        return f"<configmap {nome} ilegível: {data}>"
    return data.get(chave, f"<chave {chave} ausente no configmap {nome}>")


def ambiente(lado, deployment, container):
    deploy = kubectl(lado, "get", "deployment", deployment)
    cache = {}
    imagens, env = {}, {}
    for c in deploy["spec"]["template"]["spec"]["containers"]:
        if container and c["name"] != container:
            continue
        imagens[c["name"]] = c.get("image", "")
        prefixo = "" if container else f"{c['name']}:"
        for fonte in c.get("envFrom", []):
            pre = fonte.get("prefix", "")
            if "configMapRef" in fonte:
                nome = fonte["configMapRef"]["name"]
                data = ler_configmap(lado, nome, cache)
                if isinstance(data, Exception):
                    env[f"{prefixo}{pre}*"] = f"<configmap {nome} ilegível: {data}>"
                    continue
                for k, v in data.items():
                    env[prefixo + pre + k] = v
            elif "secretRef" in fonte:
                env[f"{prefixo}{pre}*"] = f"secret:{fonte['secretRef']['name']}/*"
        for e in c.get("env", []):
            chave = prefixo + e["name"]
            ref = e.get("valueFrom")
            if ref is None:
                env[chave] = e.get("value", "")
            elif "configMapKeyRef" in ref:
                r = ref["configMapKeyRef"]
                env[chave] = valor_do_configmap(lado, r["name"], r["key"], cache)
            elif "secretKeyRef" in ref:
                r = ref["secretKeyRef"]
                env[chave] = f"secret:{r['name']}/{r['key']}"
            elif "fieldRef" in ref:
                env[chave] = f"field:{ref['fieldRef']['fieldPath']}"
            else:
                env[chave] = f"ref:{json.dumps(ref, sort_keys=True)}"
    return imagens, env


def exibir(chave, valor):
    return "***" if CREDENCIAL.search(chave) and not str(valor).startswith("secret:") else valor


def main():
    p = argparse.ArgumentParser(description="Diff de env de um Deployment entre dois ambientes (somente leitura).")
    p.add_argument("deployment")
    p.add_argument("--a", nargs=3, required=True, metavar=("KUBECONFIG", "CONTEXTO", "NAMESPACE"))
    p.add_argument("--b", nargs=3, required=True, metavar=("KUBECONFIG", "CONTEXTO", "NAMESPACE"))
    p.add_argument("--container")
    args = p.parse_args()

    lados = {}
    for rotulo, lado in (("A", args.a), ("B", args.b)):
        try:
            lados[rotulo] = ambiente(lado, args.deployment, args.container)
        except RuntimeError as e:
            sys.exit(f"{rotulo} ({lado[1]}/{lado[2]}): não foi possível ler deployment/{args.deployment}: {e}")

    (img_a, env_a), (img_b, env_b) = lados["A"], lados["B"]
    print(f"A = {args.a[1]}/{args.a[2]}   B = {args.b[1]}/{args.b[2]}\n")
    print("== Imagens")
    for nome in sorted(img_a.keys() | img_b.keys()):
        a, b = img_a.get(nome, "-"), img_b.get(nome, "-")
        print(f"{'  ' if a == b else '≠ '}{nome}: A={a}  B={b}")

    so_a = sorted(env_a.keys() - env_b.keys())
    so_b = sorted(env_b.keys() - env_a.keys())
    diferentes = sorted(k for k in env_a.keys() & env_b.keys() if env_a[k] != env_b[k])

    print(f"\n== Só em A ({len(so_a)})")
    for k in so_a:
        print(f"  {k}={exibir(k, env_a[k])}")
    print(f"\n== Só em B ({len(so_b)})")
    for k in so_b:
        print(f"  {k}={exibir(k, env_b[k])}")
    print(f"\n== Diferentes ({len(diferentes)})")
    for k in diferentes:
        if exibir(k, env_a[k]) == "***":
            print(f"  {k}: valores diferentes (mascarado)")
        else:
            print(f"  {k}:\n    A={env_a[k]}\n    B={env_b[k]}")
    print(f"\nIguais: {len(env_a.keys() & env_b.keys()) - len(diferentes)}")


if __name__ == "__main__":
    main()
