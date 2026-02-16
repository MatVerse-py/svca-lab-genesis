#!/usr/bin/env python3.11
"""
build_artifact.py - Gerador de artefato Genesis

Pipeline causal: build → verify → artifact
Este script é a terceira etapa.

Política CORE B DAY:
- Só executa se .verify_passed existir
- Cria artefato Genesis imutável
- Registra Ohash no ledger
- Produz bundle verificável
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.absolute() / "src"))

from puf.simulated_puf import SimulatedPUF
from fuzzy_extractor.fuzzy_extractor import FuzzyExtractor
from ohash.ohash import Ohash, OhashLedger
from genesis.genesis_artifact import GenesisArtifact


def check_verify_passed() -> bool:
    """Verifica se .verify_passed existe"""
    return Path(".verify_passed").exists()


def read_verify_stamp() -> dict:
    """Lê carimbo de verificação"""
    with open(".verify_passed", "r") as f:
        lines = f.readlines()
    
    stamp = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            stamp[key.strip()] = value.strip()
    
    return stamp


def collect_source_files() -> dict:
    """Coleta todos os arquivos fonte"""
    files = {}
    
    base_path = Path(__file__).parent.absolute()
    src_path = base_path / "src"
    for py_file in src_path.rglob("*.py"):
        rel_path = py_file.relative_to(base_path)
        with open(py_file, "rb") as f:
            files[str(rel_path)] = f.read()
    
    return files


def main():
    print("=== SVCA Lab Artifact Builder ===\n")
    
    # 1. Verifica carimbo .verify_passed
    print("[1/6] Verificando carimbo de verificação...")
    if not check_verify_passed():
        print("❌ ERRO: .verify_passed não encontrado")
        print("\nPipeline causal bloqueado:")
        print("  sem verify PASS → sem artifact → sem publisher → sem DOI")
        print("\nExecute ./verify.sh primeiro")
        sys.exit(1)
    
    stamp = read_verify_stamp()
    print(f"✓ Verificação passou em {stamp.get('Timestamp', 'unknown')}")
    
    # 2. Cria PUF simulado
    print("\n[2/6] Gerando identidade física (PUF)...")
    puf = SimulatedPUF(seed=42, entropy_bits=256.0, ber=0.02)
    puf_response = puf.generate()
    print(f"✓ PUF ID: {puf.get_id()}")
    print(f"  Entropia: {puf_response.entropy_bits} bits")
    print(f"  BER: {puf_response.bit_error_rate:.4f}")
    
    # 3. Extrai chave com Fuzzy Extractor
    print("\n[3/6] Extraindo chave criptográfica...")
    fuzzy = FuzzyExtractor(key_length=32, error_tolerance=8)
    private_key, helper_data = fuzzy.gen(puf_response.response)
    print(f"✓ Chave extraída: {len(private_key)} bytes")
    
    # 4. Cria Ohash
    print("\n[4/6] Criando identidade pública (Ohash)...")
    ohash_system = Ohash(algorithm="sha3-256")
    ohash_record = ohash_system.create_record(
        private_key=private_key,
        puf_id=puf.get_id(),
        entropy_bits=puf_response.entropy_bits,
        metadata={
            "ber": puf_response.bit_error_rate,
            "puf_type": "SimulatedPUF",
            "lab_version": "0.1.0"
        }
    )
    print(f"✓ Ohash: {ohash_record.ohash[:32]}...")
    
    # 5. Registra no ledger
    print("\n[5/6] Registrando no ledger...")
    ledger = OhashLedger()
    if ledger.register(ohash_record):
        print(f"✓ Registrado no ledger (simulado)")
    else:
        print("❌ Falha ao registrar (Ohash já existe)")
        sys.exit(1)
    
    # 6. Cria artefato Genesis
    print("\n[6/6] Criando artefato Genesis...")
    
    genesis = GenesisArtifact(
        puf_id=puf.get_id(),
        ohash=ohash_record.ohash,
        entropy_bits=puf_response.entropy_bits,
        experiment_name="SVCA Lab Genesis",
        experiment_description="Laboratório de ciência executável com verificação criptográfica"
    )
    
    # Adiciona arquivos fonte
    source_files = collect_source_files()
    for filename, content in source_files.items():
        genesis.add_source_file(filename, content)
    
    print(f"  Arquivos no bundle: {len(source_files)}")
    
    # Adiciona metadados
    genesis.add_metadata("verify_stamp", stamp)
    genesis.add_metadata("python_version", stamp.get("Python", "unknown"))
    genesis.add_metadata("creation_date", datetime.utcnow().isoformat() + "Z")
    
    # Finaliza
    genesis_hash = genesis.finalize()
    print(f"✓ Genesis hash: {genesis_hash[:32]}...")
    
    # Salva artefato
    artifact_dir = Path("artifact")
    artifact_dir.mkdir(exist_ok=True)
    
    artifact_file = artifact_dir / f"genesis_{genesis_hash[:16]}.json"
    genesis.save_to_file(str(artifact_file))
    print(f"✓ Artefato salvo: {artifact_file}")
    
    # Verifica integridade
    if genesis.verify():
        print("✓ Integridade verificada")
    else:
        print("❌ Falha na verificação de integridade")
        sys.exit(1)
    
    # Salva registro do ledger
    ledger_file = artifact_dir / "ledger.json"
    with open(ledger_file, "w") as f:
        json.dump({
            "records": [r.to_dict() for r in ledger.get_all_records()],
            "count": ledger.count()
        }, f, indent=2)
    print(f"✓ Ledger salvo: {ledger_file}")
    
    print("\n=== Artefato Genesis criado com sucesso ===\n")
    print("Resumo:")
    print(f"  Genesis Hash: {genesis_hash}")
    print(f"  Ohash: {ohash_record.ohash}")
    print(f"  PUF ID: {puf.get_id()}")
    print(f"  Entropia: {puf_response.entropy_bits} bits")
    print(f"  Arquivos: {len(source_files)}")
    print(f"  Localização: {artifact_file}")
    print("\nEste artefato é IMUTÁVEL e VERIFICÁVEL independentemente.")
    print("Perda da identidade física (PUF) = perda permanente de acesso.")


if __name__ == "__main__":
    main()
