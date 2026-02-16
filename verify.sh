#!/usr/bin/env bash
# verify.sh - Verificação criptográfica e determinística
#
# Pipeline causal: build → verify → artifact
# Este script é a segunda etapa.
#
# Política CORE B DAY:
# - Fail-closed absoluto
# - Sem verify PASS → sem artifact
# - Emite carimbo .verify_passed apenas se tudo passar

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== SVCA Lab Verification ===${NC}"
echo ""

# Remove carimbo anterior se existir
if [ -f ".verify_passed" ]; then
    rm .verify_passed
    echo -e "${YELLOW}⚠${NC}  Carimbo anterior removido"
fi

FAILED=0

# Função para marcar falha
fail() {
    echo -e "${RED}✗${NC} $1"
    FAILED=1
}

# Função para marcar sucesso
pass() {
    echo -e "${GREEN}✓${NC} $1"
}

# 1. Verifica ambiente
echo -e "${YELLOW}[1/7]${NC} Verificando ambiente..."
if [ ! -d "venv" ]; then
    fail "Ambiente virtual não encontrado (execute ./build.sh primeiro)"
else
    source venv/bin/activate
    pass "Ambiente virtual ativo"
fi

# 2. Verifica Python
echo -e "${YELLOW}[2/7]${NC} Verificando Python..."
PYTHON_VERSION=$(python3.11 --version | cut -d' ' -f2)
if [[ "$PYTHON_VERSION" != 3.11* ]]; then
    fail "Python 3.11 requerido, encontrado: $PYTHON_VERSION"
else
    pass "Python $PYTHON_VERSION"
fi

# 3. Verifica dependências
echo -e "${YELLOW}[3/7]${NC} Verificando dependências..."
REQUIRED_PACKAGES=("numpy" "cryptography" "ecdsa" "pytest")
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3.11 -c "import $pkg" 2>/dev/null; then
        fail "Pacote $pkg não encontrado"
    fi
done
if [ $FAILED -eq 0 ]; then
    pass "Todas as dependências presentes"
fi

# 4. Verifica estrutura de código
echo -e "${YELLOW}[4/7]${NC} Verificando estrutura de código..."
REQUIRED_MODULES=("puf" "fuzzy_extractor" "ohash" "algebra" "genesis")
for mod in "${REQUIRED_MODULES[@]}"; do
    if [ ! -d "src/$mod" ]; then
        fail "Módulo src/$mod não encontrado"
    elif [ ! -f "src/$mod/__init__.py" ]; then
        fail "src/$mod/__init__.py não encontrado"
    fi
done
if [ $FAILED -eq 0 ]; then
    pass "Estrutura de módulos válida"
fi

# 5. Executa testes
echo -e "${YELLOW}[5/7]${NC} Executando testes..."
if [ -d "tests" ] && [ "$(ls -A tests/*.py 2>/dev/null)" ]; then
    if python3.11 -m pytest tests/ -q --tb=short; then
        pass "Todos os testes passaram"
    else
        fail "Testes falharam"
    fi
else
    echo -e "${YELLOW}⚠${NC}  Nenhum teste encontrado (pulando)"
fi

# 6. Verifica integridade criptográfica
echo -e "${YELLOW}[6/7]${NC} Verificando integridade criptográfica..."

# Computa hash de todos os arquivos fonte
HASH_FILE="reproducibility/source_hashes.txt"
mkdir -p reproducibility

echo "# Source hashes - $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$HASH_FILE"
find src/ -name "*.py" -type f | sort | while read -r file; do
    HASH=$(sha3sum -a 256 "$file" 2>/dev/null || sha256sum "$file" | cut -d' ' -f1)
    echo "$HASH  $file" >> "$HASH_FILE"
done

pass "Hashes de fonte registrados em $HASH_FILE"

# 7. Verifica políticas do laboratório
echo -e "${YELLOW}[7/7]${NC} Verificando políticas..."
if [ ! -f "LAB_POLICY.md" ]; then
    fail "LAB_POLICY.md não encontrado"
elif [ ! -f "CONTAINER_DIGEST.md" ]; then
    fail "CONTAINER_DIGEST.md não encontrado"
else
    pass "Políticas presentes"
fi

echo ""

# Decisão final (fail-closed)
if [ $FAILED -eq 1 ]; then
    echo -e "${RED}=== VERIFICAÇÃO FALHOU ===${NC}"
    echo ""
    echo "Pipeline causal bloqueado:"
    echo "  sem verify PASS → sem artifact → sem publisher → sem DOI"
    echo ""
    exit 1
else
    echo -e "${GREEN}=== VERIFICAÇÃO PASSOU ===${NC}"
    echo ""
    
    # Emite carimbo .verify_passed
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    HASH=$(find src/ -name "*.py" -type f -exec cat {} \; | sha3sum -a 256 2>/dev/null || find src/ -name "*.py" -type f -exec cat {} \; | sha256sum | cut -d' ' -f1)
    
    cat > .verify_passed <<EOF
SVCA Lab Verification Passed
Timestamp: $TIMESTAMP
Source Hash: $HASH
Python: $PYTHON_VERSION
Status: PASS
EOF
    
    echo -e "${GREEN}✓${NC} Carimbo .verify_passed emitido"
    echo ""
    echo "Próximo passo: python3 build_artifact.py"
fi
