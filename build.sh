#!/usr/bin/env bash
# build.sh - Constrói ambiente e experimentos do svca-lab
#
# Pipeline causal: build → verify → artifact
# Este script é a primeira etapa.

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== SVCA Lab Build ===${NC}"
echo ""

# Verifica Python
echo -e "${YELLOW}[1/5]${NC} Verificando Python..."
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}ERRO: Python 3.11 não encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python3.11 --version)"

# Verifica/cria ambiente virtual
echo -e "${YELLOW}[2/5]${NC} Verificando ambiente virtual..."
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3.11 -m venv venv
fi
source venv/bin/activate
echo -e "${GREEN}✓${NC} Ambiente virtual ativo"

# Instala dependências
echo -e "${YELLOW}[3/5]${NC} Instalando dependências..."
pip install -q --upgrade pip
pip install -q -e .
echo -e "${GREEN}✓${NC} Dependências instaladas"

# Verifica estrutura de diretórios
echo -e "${YELLOW}[4/5]${NC} Verificando estrutura..."
for dir in src experiments tests artifact reproducibility; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}ERRO: Diretório $dir não encontrado${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓${NC} Estrutura válida"

# Compila módulos Python
echo -e "${YELLOW}[5/5]${NC} Compilando módulos..."
python3.11 -m compileall -q src/
echo -e "${GREEN}✓${NC} Módulos compilados"

echo ""
echo -e "${GREEN}=== Build concluído com sucesso ===${NC}"
echo ""
echo "Próximo passo: ./verify.sh"
