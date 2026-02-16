import sys
import os
import time
import numpy as np
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute() / "src"))

from puf.rp2040_bridge import RP2040Bridge
from algebra.adaptive_omega import AdaptiveOmega
from algebra.psi_state import PsiState, StateVector
from genesis.genesis_artifact import GenesisArtifact

def run_experiment():
    print("🚀 Iniciando Pipeline Soberano: Hardware Real + Ω Adaptativo\n")

    # 1. Conexão com Hardware
    print("[1/4] Conectando ao Ω-PUF (RP2040)...")
    puf = RP2040Bridge()
    puf.connect()
    puf_res = puf.generate()
    puf_id = puf.get_id()
    print(f"✓ Campo físico adquirido. PUF ID: {puf_id}")

    # 2. Inicialização do Ω Adaptativo
    print("\n[2/4] Inicializando Motor de Ω Adaptativo...")
    adaptive = AdaptiveOmega()
    
    # Simulação de ciclos de adaptação (Aprendizado de Regras)
    print("  Treinando regras de admissibilidade...")
    for _ in range(10):
        # Vetor de estado simulado: [Time, Entropy, PUF, BER, Temp, Volt, Jitter, Net]
        sample_state = np.random.rand(8)
        # Outcome positivo se PUF e Entropia forem altos
        outcome = 1.0 if (sample_state[2] > 0.5 and sample_state[1] > 0.5) else 0.0
        adaptive.adapt(sample_state, outcome)
    
    rules = adaptive.get_rules_summary()
    print("✓ Regras aprendidas (Top 3):")
    sorted_rules = sorted(rules.items(), key=lambda x: x[1], reverse=True)
    for name, weight in sorted_rules[:3]:
        print(f"  - {name}: {weight:.4f}")

    # 3. Verificação de Estado Ψ
    print("\n[3/4] Validando Trajetória Ψ...")
    
    # Cria vetor de estado inicial (Genesis)
    genesis_vector = StateVector(
        puf_id=puf_id,
        timestamp=time.time(),
        entropy_bits=puf_res.entropy_bits,
        metadata={"adaptive": True}
    )
    
    psi = PsiState(genesis_vector=genesis_vector)
    
    # Tenta adicionar um novo estado baseado na admissibilidade adaptativa
    current_state_data = np.random.rand(8)
    admissibility = adaptive.calculate_admissibility(current_state_data)
    
    if admissibility > 0.5:
        print(f"✓ Estado ADMISSÍVEL (Ω-Energy: {admissibility:.4f})")
        new_vector = StateVector(
            puf_id=puf_id,
            timestamp=time.time(),
            metadata={"adaptive_score": float(admissibility)}
        )
        psi.append(new_vector)
    else:
        print(f"❌ Estado REJEITADO (Ω-Energy: {admissibility:.4f})")
        print("  Ajustando motor adaptativo para falha...")
        adaptive.adapt(current_state_data, -1.0)
        return

    # 4. Geração de Artefato Genesis
    print("\n[4/4] Selando Artefato Genesis...")
    genesis = GenesisArtifact(
        puf_id=puf_id,
        ohash=psi.compute_trajectory_hash(),
        entropy_bits=puf_res.entropy_bits,
        experiment_name="Adaptive Hardware Genesis",
        experiment_description="Fusão de Hardware Real (RP2040) com Admissibilidade Adaptativa"
    )
    
    # Salva modelo adaptativo no artefato
    model_path = "artifact/adaptive_model.json"
    os.makedirs("artifact", exist_ok=True)
    adaptive.save_model(model_path)
    
    with open(model_path, "rb") as f:
        genesis.add_source_file("adaptive_model.json", f.read())
    
    genesis_hash = genesis.finalize()
    print(f"✓ Pipeline Completo. Genesis Hash: {genesis_hash}")
    print(f"✓ Artefato salvo em artifact/")

if __name__ == "__main__":
    run_experiment()
