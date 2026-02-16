# Container Digest

## Ambiente de Execução Congelado

Este documento registra o digest criptográfico do ambiente de execução para garantir reprodutibilidade determinística.

## Sistema Operacional

- **OS**: Ubuntu 22.04 LTS
- **Kernel**: Linux 5.15+
- **Arquitetura**: x86_64 (amd64)

## Python

- **Versão**: 3.11.0rc1
- **Executável**: `/usr/bin/python3.11`
- **pip**: 23.0+

## Dependências Core

```
numpy==1.24.3
cryptography==41.0.7
pycryptodome==3.19.0
ecdsa==0.18.0
pytest==7.4.3
pytest-cov==4.1.0
```

## Hash do Ambiente

```
# Gerado em: [Genesis Event]
# Método: SHA3-256

ENVIRONMENT_HASH: [a ser calculado no Genesis]
DEPENDENCIES_HASH: [a ser calculado no Genesis]
SYSTEM_HASH: [a ser calculado no Genesis]
```

## Comandos de Verificação

### Verificar versão Python
```bash
python3.11 --version
```

### Verificar dependências
```bash
pip3 list --format=freeze | sha3sum -a 256
```

### Verificar integridade do ambiente
```bash
./verify.sh --check-environment
```

## Reprodutibilidade

Para reproduzir este ambiente exato:

```bash
# 1. Instalar Python 3.11
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# 2. Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# 3. Instalar dependências exatas
pip install -r requirements.txt

# 4. Verificar digest
./verify.sh --check-environment
```

## Fontes de Não-Determinismo Controladas

### Randomness
- Seed fixa: `SVCA_SEED=0x42` (quando aplicável)
- RNG: `numpy.random.seed(42)`

### Timestamps
- Modo replay: timestamps fixos de `reproducibility/timestamps.log`
- Modo produção: timestamps reais com triple anchor

### Localização
- Modo teste: localização fixa `(0.0, 0.0)`
- Modo produção: GPS ou IP geolocation

### Temperatura
- Modo teste: temperatura fixa `20.0°C`
- Modo produção: sensor físico ou API

## Política de Atualização

**Este ambiente é IMUTÁVEL após Genesis.**

Mudanças requerem:
1. Novo Genesis Event
2. Nova versão do laboratório
3. Registro de fork na linhagem
4. Atualização do Ohash no ledger

## Verificação de Integridade

### Checklist

- [ ] Python 3.11 instalado
- [ ] Todas as dependências com versões exatas
- [ ] Hash do ambiente corresponde ao registrado
- [ ] Testes de reprodutibilidade passam
- [ ] `.verify_passed` emitido

### Comando de Verificação Completa

```bash
./verify.sh --full-check
```

## Assinatura

```
-----BEGIN GENESIS SIGNATURE-----
[a ser gerado no Genesis Event]
-----END GENESIS SIGNATURE-----
```

## Metadados

- **Criado em**: [Genesis Event]
- **Versão do Lab**: 0.1.0
- **Protocolo**: CORE B DAY v1
- **Status**: Congelado

---

**AVISO**: Modificar este ambiente após Genesis invalida todos os artefatos gerados. Não existe recuperação.
