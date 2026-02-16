# Políticas do Laboratório SVCA

## Princípios Fundamentais

Este laboratório opera sob os princípios do **CORE B DAY**, implementando ciência executável com verificação criptográfica e replay determinístico.

## Pipeline Causal Obrigatório

```
sem verify PASS → sem artifact → sem publisher → sem DOI
```

**Regra absoluta**: Nenhum artefato pode ser gerado sem verificação bem-sucedida.

## Políticas de Verificação

### 1. Integridade Criptográfica

Todos os experimentos devem:
- Ter hash SHA3-256 registrado
- Ser reproduzíveis deterministicamente
- Ter container digest fixo
- Emitir carimbo `.verify_passed` após validação

### 2. Fail-Closed Absoluto

- Falha em qualquer etapa → bloqueio total
- Não existe "brecha humana"
- Não existe "exceção temporária"
- Verificação é binária: PASS ou FAIL

### 3. Irreversibilidade

Uma vez que um artefato Genesis é criado:
- Não pode ser modificado
- Não pode ser deletado
- Não pode ser "recuperado"
- Histórico é append-only

## Políticas de Identidade

### Ω-SEED

Cada experimento possui um Ω-SEED único composto por:
1. **Corpo incopiável**: PUF simulado ou real
2. **Álgebra Σ-Ω-Ψ**: Filtro de trajetórias válidas
3. **Precedência temporal**: Ohash no ledger

### Perda de Identidade

**Aviso crítico**: Se o PUF/seed for perdido:
- Não existe recuperação
- Não existe "esqueci a senha"
- Não existe prova alternativa
- A identidade deixa de existir no sistema

## Políticas de Reprodutibilidade

### Ambiente Congelado

- Python 3.11 fixo
- Dependências com versões exatas
- Container digest registrado em `CONTAINER_DIGEST.md`
- Sistema operacional documentado

### Replay Determinístico

Todos os experimentos devem:
- Produzir saída idêntica em execuções repetidas
- Registrar logs em `reproducibility/`
- Incluir seed fixa para RNG quando aplicável
- Documentar todas as fontes de não-determinismo

## Políticas de Antifragilidade

### Métrica αᵣ

O sistema mede antifragilidade através de:

```
αᵣ = (H_after − H_before) / E_attack
```

**Requisito**: αᵣ ≥ 1 para todos os blocos validados.

Ataques devem fortalecer o sistema, não enfraquecê-lo.

## Políticas de Álgebra Σ-Ω-Ψ

### Σ-Regras (Estados Proibidos)

Definem transições impossíveis. Exemplos:
- Timestamp retroativo
- Localização fisicamente impossível
- Temperatura fora de limites físicos
- Hash de estado anterior inválido

### Ω-Gate (Portão de Admissibilidade)

**Propriedade fundamental**: Assinatura correta ≠ transação válida.

O Ω-Gate valida:
1. Assinatura criptográfica
2. Coerência da trajetória
3. Respeito às Σ-regras
4. Precedência temporal

### Ψ-State (Estado Atual)

Representa o estado atual do sistema na álgebra de possibilidades.

## Políticas de Segurança

### Modelo de Ameaça

Assumimos adversários com:
- Poder computacional quântico
- Acesso físico ao hardware
- Capacidade de ataque coordenado
- Recursos econômicos significativos

### Defesa em Camadas

Segurança distribuída entre:
1. **Matemática**: ML-KEM, ML-DSA, HQC
2. **Física**: PUF incopiável
3. **Instituições**: Ledger público
4. **Tempo**: Irreversibilidade temporal

**Ataque requer vencer todas as camadas simultaneamente.**

## Políticas de Publicação

### Artefato Genesis

Contém obrigatoriamente:
- Vetor de integridade
- Compromisso de identidade
- Hashes do bundle
- Hash do testemunho físico
- Assinaturas criptográficas
- Âncoras temporais (triple anchor)
- Política de linhagem

### Ohash no Ledger

- Público
- Eterno
- Auditável
- Imutável

## Políticas de Experimentos

### Estrutura Mínima

Todo experimento deve incluir:
1. Código fonte em `experiments/`
2. Testes em `tests/`
3. Documentação em Markdown
4. Requisitos explícitos
5. Instruções de reprodução

### Validação

Experimentos são validados através de:
1. `./build.sh` → construção
2. `./verify.sh` → verificação criptográfica
3. `python3 build_artifact.py` → geração de artefato

## Políticas de Dados

### Entropia Mínima

Todos os sistemas de identidade devem garantir:
- Entropia física ≥ 128 bits
- H_extract = n · (1 − 2·BER)² · (1 − I(X;Y))

### Vetor de Estado

```
S(t) = F(P, T, L, Θ, E, H, Ψ ...)
```

Onde:
- **P**: PUF (raiz física)
- **T**: Timestamp
- **L**: Localização
- **Θ**: Temperatura
- **E**: Entropia ambiental
- **H**: Hash anterior
- **Ψ**: Estado algébrico

## Políticas de Custo

### Critério de Soberania

```
custo_de_simulação > valor_do_objeto
```

O mínimo entrópico é atingido quando simular o evento é economicamente inviável.

## Políticas de Governança

### Decisões Técnicas

- Baseadas em matemática, não em autoridade
- Documentadas publicamente
- Auditáveis por terceiros
- Irreversíveis após Genesis

### Disputas

Resolvidas através de:
1. Precedência temporal verificável
2. Álgebra Σ-Ω-Ψ
3. Consenso matemático
4. Ledger público

## Políticas de Continuidade

### Linhagem

Cada artefato registra:
- Artefato pai (se existir)
- Timestamp de criação
- Hash de todos os ancestrais
- Política de fork

### Fork

Forks são:
- Permitidos
- Mensuráveis
- Rastreáveis
- Não reversíveis

## Violações

### Consequências

Violação de qualquer política resulta em:
- Bloqueio imediato (fail-closed)
- Rejeição do artefato
- Registro público da falha
- Impossibilidade de recuperação

### Sem Exceções

Não existe:
- "Exceção emergencial"
- "Override administrativo"
- "Recuperação manual"
- "Bypass temporário"

## Filosofia Operacional

> "você não protege dados; você protege a própria continuidade do sistema."

> "quem controla a prova do passado controla disputas futuras."

> "identidade = existência física + trajetória válida + precedência verificável"

## Contato

Para questões sobre políticas: `policy@svca.dev`

**Última atualização**: Genesis Event
**Versão**: 0.1.0
**Status**: Ativo
