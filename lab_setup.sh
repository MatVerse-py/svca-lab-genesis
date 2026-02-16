#!/usr/bin/env bash
# lab_setup.sh - Ativação limpa do laboratório SVCA
#
# Executa sequência completa: build → verify → artifact

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗██╗   ██╗ ██████╗ █████╗       ██╗      █████╗ ██████╗  ║
║   ██╔════╝██║   ██║██╔════╝██╔══██╗      ██║     ██╔══██╗██╔══██╗ ║
║   ███████╗██║   ██║██║     ███████║█████╗██║     ███████║██████╔╝ ║
║   ╚════██║╚██╗ ██╔╝██║     ██╔══██║╚════╝██║     ██╔══██║██╔══██╗ ║
║   ███████║ ╚████╔╝ ╚██████╗██║  ██║      ███████╗██║  ██║██████╔╝ ║
║   ╚══════╝  ╚═══╝   ╚═════╝╚═╝  ╚═╝      ╚══════╝╚═╝  ╚═╝╚═════╝  ║
║                                                           ║
║   Laboratório de Ciência Executável                      ║
║   Verificação Criptográfica | Replay Determinístico     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}Protocolo: CORE B DAY${NC}"
echo -e "${BLUE}Versão: 0.1.0${NC}"
echo ""

# Verifica se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}ERRO: Execute este script no diretório raiz do svca-lab${NC}"
    exit 1
fi

echo -e "${YELLOW}Pipeline causal obrigatório:${NC}"
echo "  build → verify → artifact"
echo ""

# Etapa 1: Build
echo -e "${CYAN}═══ Etapa 1/3: Build ═══${NC}"
if ./build.sh; then
    echo ""
else
    echo -e "${RED}Build falhou. Abortando.${NC}"
    exit 1
fi

# Etapa 2: Verify
echo -e "${CYAN}═══ Etapa 2/3: Verify ═══${NC}"
if ./verify.sh; then
    echo ""
else
    echo -e "${RED}Verificação falhou. Abortando.${NC}"
    echo "Pipeline causal bloqueado:"
    echo "  sem verify PASS → sem artifact → sem publisher → sem DOI"
    exit 1
fi

# Etapa 3: Artifact
echo -e "${CYAN}═══ Etapa 3/3: Artifact ═══${NC}"
if python3.11 build_artifact.py; then
    echo ""
else
    echo -e "${RED}Criação de artefato falhou.${NC}"
    exit 1
fi

# Sucesso
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ✓ Laboratório ativado com sucesso                      ║
║                                                           ║
║   Artefato Genesis criado e verificado                   ║
║   Identidade registrada no ledger                        ║
║   Pipeline causal completo                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo "Próximos passos:"
echo "  1. Explorar experimentos em experiments/"
echo "  2. Executar testes com pytest"
echo "  3. Consultar documentação em README.md"
echo ""
echo -e "${YELLOW}AVISO:${NC} Perda da identidade física (PUF) = perda permanente."
echo "Não existe recuperação. Não existe 'esqueci a senha'."
