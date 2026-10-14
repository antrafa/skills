# Armadilhas que custam tempo

Leia antes de improvisar. Cada item aqui é um erro que parece certo na hora,
passa em revisão e só se mostra depois do deploy. Quando uma armadilha nova
custar tempo de verdade numa sessão, proponha ao usuário acrescentá-la aqui,
com o sintoma que ela produz e como evitar.

## `kubectl apply` não apaga o que saiu do arquivo

`apply` cria e atualiza; não remove. Renomear um recurso no manifest (o
`metadata.name` de um Service, ConfigMap, Secret ou VirtualService) cria o
novo e deixa o antigo vivo no cluster. Com rotas, o órfão pode continuar
atendendo: duas VirtualServices para o mesmo host e prefixo entram em
conflito, e qual delas atende não é algo em que dê para confiar.

- Ao renomear, entregue também o `kubectl delete` do nome antigo, como passo
  separado e com confirmação.
- Com Helm isso não acontece: o `helm upgrade` remove o que saiu do chart.
  Misturar `apply` manual com recursos de um release cria exatamente esse
  tipo de sobra.

## O cluster não é o git

ConfigMap e Secret editados à mão, réplicas zeradas de propósito, imagem
trocada por um `set image` de emergência: o estado vivo diverge do
repositório sem deixar rastro no git. Aplicar o arquivo "como está" desfaz
essas mudanças sem aviso.

- Antes de aplicar em ambiente em uso, o usuário roda `kubectl diff -f`
  (ou `helm diff upgrade`) e lê cada diferença.
- Secret marcado como alterado no diff é um valor manual que o apply vai
  sobrescrever — às vezes com vazio. Pergunte antes.
- `replicas` diferente pode ser decisão de alguém (desligamento,
  manutenção), não drift a corrigir.

## Variável não definida vira texto vazio

`envsubst`, `${VAR}` em shell e a maioria dos templates trocam variável
inexistente por string vazia, sem erro. O manifest renderiza, o apply passa,
e o pod sobe com `DB_URL=` ou uma imagem `registry/app:`.

- Renderize e leia antes de aplicar; procure `: $`, `=$` e `:""` no
  resultado.
- Em shell, `set -u` faz o script falhar na variável não definida.
- No `envsubst`, passe a lista explícita (`envsubst '$IMAGE $TAG'`) para não
  apagar `$` que deviam ficar literais.

## Base64 não é proteção

O que está em `Secret.data` é só codificado. `get secret -o yaml`, um
`values.yaml` com senha ou um `.env` com `*_ENCODED` commitado expõem a
credencial do mesmo jeito que texto puro.

## Mensagem de commit que dispara pipeline

Pipelines que reagem a um marcador na mensagem de commit (`[deploy]`,
`[skip ci]`, `[upgrade ...]`) disparam também com commit manual que repete o
marcador por acaso ou por cópia. Antes de escrever a mensagem, confira as
`rules` do `.gitlab-ci.yml` (ou equivalente) por `$CI_COMMIT_MESSAGE`.

## Repositório de ambiente que o pipeline também altera

Quando o pipeline commita no próprio repositório de configuração (bump de
tag de imagem, por exemplo), editar sobre um clone antigo e aplicar faz o
ambiente voltar para a versão anterior. Atualize (`git pull --ff-only`) antes
de editar, e de novo antes de aplicar.

## Rede corporativa e comandos que nunca terminam

DNS lento, proxy e firewall fazem `git`, `curl`, `helm repo update` e
`docker pull` ficarem pendurados sem erro. Use timeout explícito
(`timeout 30 <cmd>`, `curl -m 15`) e trate o timeout como informação: rede,
não ferramenta quebrada.
