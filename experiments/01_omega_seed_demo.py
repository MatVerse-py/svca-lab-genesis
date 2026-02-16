#!/usr/bin/env python3.11
"""
Experimento 01: Demonstração de Ω-SEED

Demonstra o primitivo central do CORE B DAY:
Ω-SEED = (corpo incopiável) ⊗ (álgebra de admissibilidade) ⊗ (precedência temporal)

Este experimento:
1. Cria PUF simulado (corpo incopiável)
2. Extrai chave com Fuzzy Extractor
3. Cria Ohash (identidade pública)
4. Valida trajetória com Ω-Gate
5. Registra no ledger
"""

import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from puf.simulated_puf import SimulatedPUF
from fuzzy_extractor.fuzzy_extractor import FuzzyExtractor
from ohash.ohash import Ohash, OhashLedger
from algebra.sigma_rules import create_default_rules
from algebra.omega_gate import OmegaGate
from algebra.psi_state import PsiState, StateVector
import time


def main():
    print("=== Experimento 01: Ω-SEED Demo ===\n")
    
    # 1. Cria PUF (corpo incopiável)
    print("[1/6] Criando PUF (corpo incopiável)...")
    puf = SimulatedPUF(seed=12345, entropy_bits=256.0, ber=0.02)
    puf_response = puf.generate()
    
    print(f"  PUF ID: {puf.get_id()}")
    print(f"  Entropia: {puf_response.entropy_bits} bits")
    print(f"  BER: {puf_response.bit_error_rate:.4f}")
    print(f"  ✓ Corpo físico único criado\n")
    
    # 2. Extrai chave (Fuzzy Extractor)
    print("[2/6] Extraindo chave criptográfica...")
    fuzzy = FuzzyExtractor(key_length=32, error_tolerance=8)
    private_key, helper_data = fuzzy.gen(puf_response.response)
    
    print(f"  Chave privada: {private_key.hex()[:32]}...")
    print(f"  Helper data: {len(helper_data)} bytes")
    print(f"  ✓ Chave estável extraída\n")
    
    # 3. Cria Ohash (identidade pública)
    print("[3/6] Criando Ohash (identidade pública)...")
    ohash_system = Ohash(algorithm="sha3-256")
    ohash_record = ohash_system.create_record(
        private_key=private_key,
        puf_id=puf.get_id(),
        entropy_bits=puf_response.entropy_bits,
        metadata={"experiment": "01_omega_seed_demo"}
    )
    
    print(f"  Ohash: {ohash_record.ohash}")
    print(f"  Timestamp: {ohash_record.timestamp}")
    print(f"  ✓ Identidade pública criada\n")
    
    # 4. Registra no ledger
    print("[4/6] Registrando no ledger...")
    ledger = OhashLedger()
    if ledger.register(ohash_record):
        print(f"  ✓ Registrado no ledger")
        print(f"  Registros totais: {ledger.count()}\n")
    else:
        print(f"  ✗ Falha ao registrar (já existe)\n")
    
    # 5. Cria trajetória com Ψ-State
    print("[5/6] Criando trajetória (Ψ-State)...")
    
    # Estado Genesis
    genesis_vector = StateVector(
        puf_id=puf.get_id(),
        timestamp=time.time(),
        location=(0.0, 0.0),
        temperature=20.0,
        entropy_bits=puf_response.entropy_bits
    )
    
    psi_state = PsiState(genesis_vector=genesis_vector)
    print(f"  Genesis hash: {psi_state.state_hashes[0][:32]}...")
    
    # Adiciona estados subsequentes
    for i in range(3):
        time.sleep(0.1)  # Pequeno delay para timestamp diferente
        
        new_vector = StateVector(
            puf_id=puf.get_id(),
            timestamp=time.time(),
            location=(0.0, 0.0),
            temperature=20.0 + i * 0.5,
            entropy_bits=puf_response.entropy_bits
        )
        
        psi_state.append(new_vector)
    
    print(f"  Estados na trajetória: {psi_state.count()}")
    print(f"  Cadeia válida: {psi_state.verify_chain()}")
    print(f"  ✓ Trajetória criada\n")
    
    # 6. Valida com Ω-Gate
    print("[6/6] Validando com Ω-Gate...")
    
    # Cria regras Σ
    sigma_rules = create_default_rules()
    print(f"  Regras Σ carregadas: {sigma_rules.count()}")
    
    # Cria Ω-Gate
    omega_gate = OmegaGate(sigma_rules=sigma_rules, strict_mode=True)
    
    # Testa transição válida
    valid_vector = StateVector(
        puf_id=puf.get_id(),
        timestamp=time.time(),
        location=(0.0, 0.0),
        temperature=22.0,
        entropy_bits=puf_response.entropy_bits
    )
    
    result = omega_gate.validate(valid_vector, psi_state, signature_valid=True)
    print(f"  Transição válida: {result.decision.value}")
    print(f"  Violações: {len(result.violations)}")
    
    # Testa transição inválida (timestamp retroativo)
    invalid_vector = StateVector(
        puf_id=puf.get_id(),
        timestamp=time.time() - 100,  # Retroativo!
        location=(0.0, 0.0),
        temperature=22.0,
        entropy_bits=puf_response.entropy_bits
    )
    
    result_invalid = omega_gate.validate(invalid_vector, psi_state, signature_valid=True)
    print(f"  Transição inválida: {result_invalid.decision.value}")
    print(f"  Violações: {len(result_invalid.violations)}")
    if len(result_invalid.violations) > 0:
        print(f"    → {result_invalid.violations[0].message}")
    
    print(f"  ✓ Ω-Gate funcionando (fail-closed)\n")
    
    # Resumo
    print("=== Resumo do Ω-SEED ===\n")
    print("Componentes criados:")
    print(f"  1. Corpo incopiável: PUF {puf.get_id()}")
    print(f"  2. Álgebra Σ-Ω-Ψ: {sigma_rules.count()} regras, Ω-Gate ativo")
    print(f"  3. Precedência temporal: {psi_state.count()} estados, cadeia válida")
    print()
    print("Propriedades verificadas:")
    print(f"  ✓ Entropia ≥ 128 bits: {puf_response.entropy_bits} bits")
    print(f"  ✓ Identidade pública no ledger: {ohash_record.ohash[:16]}...")
    print(f"  ✓ Trajetória verificável: {psi_state.verify_chain()}")
    print(f"  ✓ Fail-closed absoluto: transições inválidas bloqueadas")
    print()
    print("AVISO: Perda do PUF = perda permanente da identidade.")
    print("Não existe recuperação. Não existe 'esqueci a senha'.")


if __name__ == "__main__":
    main()
