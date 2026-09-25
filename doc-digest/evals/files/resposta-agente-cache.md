Boa pergunta! Analisei o `ConsultaProcessoService` e o fluxo de consulta, e dá para resolver a lentidão com cache. Vou explicar o diagnóstico, a proposta e como implementar.

## Diagnóstico

Hoje cada chamada a `GET /api/processos/{numero}/movimentacoes` faz três coisas em sequência:

1. Busca o processo no Oracle (`ProcessoRepository.findByNumero`), em torno de 40 ms.
2. Chama o serviço externo do tribunal (`TribunalClient.listarMovimentacoes`) para trazer as movimentações atualizadas, entre 800 ms e 2,5 s dependendo do tribunal.
3. Monta o DTO de resposta, juntando as movimentações com os dados do processo.

O gargalo claramente é o passo 2. Nos logs de ontem, 92% do tempo de resposta estava na chamada ao tribunal, e o mesmo processo é consultado muitas vezes seguidas: o escritório abre a tela, atualiza, outro advogado abre a mesma tela. Olhando o access log, os 200 processos mais consultados respondem por cerca de 70% das requisições.

Um ponto importante do negócio, que você comentou na issue: o advogado precisa ver a movimentação assim que ela é publicada pelo tribunal, porque alguns prazos começam a contar no dia da publicação. Então qualquer solução precisa manter os dados sempre atualizados em tempo real.

## Proposta

A ideia é colocar um cache na frente do `TribunalClient`, guardando a lista de movimentações por número de processo.

### Por que Caffeine

Considerei três opções:

- **Redis**: resolve bem, mas exige subir e operar mais um componente, e a equipe não tem Redis em produção hoje.
- **Cache no banco (tabela de movimentações)**: daria para consultar offline, mas duplica dado do tribunal e cria um problema de sincronização.
- **Caffeine (cache em memória)**: já vem no Spring Boot via `spring-boot-starter-cache`, zero infraestrutura nova, latência de microssegundos.

Fui de Caffeine pela simplicidade. Para o volume atual, cache local resolve.

### Configuração

A configuração sugerida:

```yaml
spring:
  cache:
    type: caffeine
    cache-names: movimentacoes
    caffeine:
      spec: maximumSize=5000,expireAfterWrite=24h
```

O TTL de 24 horas foi escolhido porque o tribunal publica as movimentações em lote durante a madrugada, então um dia de cache cobre o ciclo inteiro e maximiza o hit rate. O limite de 5000 entradas cobre com folga os processos mais consultados.

### Código

No serviço, basta anotar o método:

```java
@Service
public class ConsultaProcessoService {

    private final TribunalClient tribunalClient;
    private final ProcessoRepository processoRepository;

    @Cacheable(value = "movimentacoes", key = "#numero")
    public List<Movimentacao> listarMovimentacoes(String numero) {
        return tribunalClient.listarMovimentacoes(numero);
    }
}
```

E habilitar o cache na aplicação:

```java
@SpringBootApplication
@EnableCaching
public class ConsultaApplication { }
```

Atenção: o `@Cacheable` só funciona quando o método é chamado de fora da classe, por causa do proxy do Spring. Se o controller chama `listarMovimentacoes` direto no service, está ok.

## Impacto esperado

Com hit rate estimado de 70% (os 200 processos mais consultados), o tempo médio de resposta deve cair de cerca de 1,6 s para algo perto de 500 ms. O p95, que hoje passa de 2 s, deve ficar abaixo de 1 s para os processos quentes.

Também reduz a carga no serviço do tribunal, que já nos devolveu HTTP 429 algumas vezes no mês passado.

## Deploy

A aplicação roda hoje com 3 réplicas no cluster, atrás do ingress. Não precisa mudar nada no deploy: é só subir a nova versão normalmente pela pipeline. A mudança é pequena e não mexe em banco.

## Próximos passos

1. Adicionar a dependência `com.github.ben-manes.caffeine:caffeine` no `pom.xml`.
2. Aplicar a configuração e as anotações acima.
3. Subir em homologação e comparar o tempo de resposta com o de hoje.
4. Se estiver tudo certo, subir em produção.

Se quiser, posso já abrir o MR com essas mudanças. Qualquer dúvida é só falar!
