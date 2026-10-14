# Revisão red team / blue team

Dois revisores analisam a mesma mudança com objetivos opostos. O blue team
verifica se ela resolve o que foi combinado. O red team tenta provar que ela
está errada. A independência é o que dá valor ao método: um revisor que lê a
conclusão do outro tende a concordar com ela.

## Material para os dois

Os dois recebem o mesmo pacote, e nada além dele:

- descrição original do problema;
- plano combinado com o usuário (regra 18);
- diff completo da mudança (`git diff <base>`, incluindo o que não foi
  commitado);
- testes criados e a saída da última execução.

## Blue team — validar

- Cada item do plano está implementado e coberto por teste?
- Os testes exercitam o comportamento ou só passam? Assertion fraca e mock que
  devolve exatamente o esperado sem passar pela lógica são os casos comuns.
- Quem mais usa o código alterado? Esses chamadores continuam cobertos?
- A mudança segue o estilo e os padrões que já existem no repositório?

## Red team — atacar

Cético de propósito:

- A causa corrigida é a raiz ou um sintoma dela?
- Entradas que quebram: nulo, lista vazia, valor-limite, data e fuso
  horário, encoding, número grande, concorrência, timeout, rede fora.
- Segurança: autorização, validação de entrada, dado exposto em resposta ou
  log.
- Efeito colateral em outras telas, endpoints, jobs ou consumidores da API.
- Existe solução mais simples ou mais segura que foi descartada cedo demais?
- Algum teste passa pelo motivo errado?

Quando der, o red team demonstra a falha com um teste rápido em diretório
temporário, fora do repositório e sem tocar no código de produção.

## Execução

**Com subagentes:** disparar os dois em paralelo, cada um com o pacote e só a
própria missão. São revisões de leitura; o prompt diz explicitamente que não
podem editar arquivo do repositório, commitar nem rodar comando que altere
estado.

**Sem subagentes:** em sequência, primeiro o red e depois o blue, em seções
separadas, assumindo de verdade a postura de cada um.

## Retorno de cada time

- Veredito: `sólida`, `sólida com ressalvas` ou `problemática`.
- Achados, cada um com severidade (alta, média ou baixa), evidência (arquivo e
  linha, teste ou saída) e sugestão.

## Síntese para o usuário

1. Onde os dois concordam — a parte mais confiável.
2. Onde discordam, qual lado parece ter razão e por quê.
3. Achados de severidade alta primeiro.
4. Recomendação final: manter, ajustar ou repensar.

Nenhuma correção é aplicada aqui. O que a revisão sugerir volta para
discussão e espera nova aprovação.
