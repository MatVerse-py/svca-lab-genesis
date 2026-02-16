"""
Genesis Artifact - Artefato de origem verificável

Implementa evento Genesis irreversível que torna origem
externamente verificável.

CORE B DAY:
"Genesis é o evento irreversível em que a origem de um sistema
se torna externamente verificável."

Depois disso:
- O passado fica restrito
- Forks tornam-se mensuráveis
- Disputas viram matemáticas
"""

import hashlib
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from .triple_anchor import TripleAnchor


@dataclass
class GenesisBundle:
    """
    Bundle de arquivos do artefato Genesis
    
    Contém todos os arquivos que compõem o experimento.
    """
    
    files: Dict[str, bytes] = field(default_factory=dict)
    """Dicionário filename -> conteúdo"""
    
    def add_file(self, filename: str, content: bytes) -> None:
        """Adiciona arquivo ao bundle"""
        self.files[filename] = content
    
    def compute_file_hash(self, filename: str) -> str:
        """Computa hash de arquivo específico"""
        if filename not in self.files:
            raise ValueError(f"Arquivo não encontrado: {filename}")
        
        h = hashlib.sha3_256()
        h.update(self.files[filename])
        return h.hexdigest()
    
    def compute_bundle_hash(self) -> str:
        """Computa hash do bundle completo"""
        h = hashlib.sha3_256()
        h.update(b"GENESIS_BUNDLE")
        
        # Ordena arquivos para garantir determinismo
        for filename in sorted(self.files.keys()):
            h.update(filename.encode())
            h.update(self.files[filename])
        
        return h.hexdigest()
    
    def get_manifest(self) -> Dict[str, str]:
        """Retorna manifesto com hash de cada arquivo"""
        return {
            filename: self.compute_file_hash(filename)
            for filename in self.files.keys()
        }


class GenesisArtifact:
    """
    Artefato Genesis
    
    Estrutura completa do evento Genesis:
    - Vetor de integridade
    - Compromisso de identidade
    - Hashes do bundle
    - Hash do testemunho físico
    - Assinaturas
    - Âncoras temporais (triple anchor)
    - Política de linhagem
    """
    
    def __init__(
        self,
        puf_id: str,
        ohash: str,
        entropy_bits: float,
        experiment_name: str,
        experiment_description: str
    ):
        """
        Inicializa artefato Genesis
        
        Args:
            puf_id: ID do PUF (raiz física)
            ohash: Ohash da identidade
            entropy_bits: Entropia da identidade
            experiment_name: Nome do experimento
            experiment_description: Descrição do experimento
        """
        self.puf_id = puf_id
        self.ohash = ohash
        self.entropy_bits = entropy_bits
        self.experiment_name = experiment_name
        self.experiment_description = experiment_description
        
        # Componentes do artefato
        self.bundle = GenesisBundle()
        self.triple_anchor = TripleAnchor()
        self.signatures: List[str] = []
        self.metadata: Dict[str, Any] = {}
        
        # Estado
        self.finalized = False
        self.genesis_hash: Optional[str] = None
    
    def add_source_file(self, filename: str, content: bytes) -> None:
        """
        Adiciona arquivo fonte ao bundle
        
        Args:
            filename: Nome do arquivo
            content: Conteúdo em bytes
        """
        if self.finalized:
            raise RuntimeError("Artefato já finalizado, não pode adicionar arquivos")
        
        self.bundle.add_file(filename, content)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Adiciona metadado ao artefato
        
        Args:
            key: Chave do metadado
            value: Valor (deve ser serializável em JSON)
        """
        if self.finalized:
            raise RuntimeError("Artefato já finalizado, não pode adicionar metadados")
        
        self.metadata[key] = value
    
    def finalize(self) -> str:
        """
        Finaliza artefato Genesis
        
        Cria âncoras temporais, computa hashes finais e torna imutável.
        
        Returns:
            Genesis hash (identificador único do artefato)
        """
        if self.finalized:
            raise RuntimeError("Artefato já finalizado")
        
        # 1. Cria triple anchor
        self.triple_anchor.create_all()
        
        # 2. Computa genesis hash
        self.genesis_hash = self._compute_genesis_hash()
        
        # 3. Marca como finalizado (imutável)
        self.finalized = True
        
        return self.genesis_hash
    
    def _compute_genesis_hash(self) -> str:
        """
        Computa hash Genesis
        
        Combina todos os componentes do artefato em hash único.
        
        Returns:
            Genesis hash
        """
        h = hashlib.sha3_256()
        
        # Prefixo de domínio
        h.update(b"SVCA_GENESIS_V1")
        
        # Identidade
        h.update(self.puf_id.encode())
        h.update(self.ohash.encode())
        h.update(str(self.entropy_bits).encode())
        
        # Experimento
        h.update(self.experiment_name.encode())
        h.update(self.experiment_description.encode())
        
        # Bundle
        h.update(self.bundle.compute_bundle_hash().encode())
        
        # Triple anchor
        h.update(self.triple_anchor.compute_hash().encode())
        
        # Metadados (ordenados para determinismo)
        for key in sorted(self.metadata.keys()):
            h.update(key.encode())
            h.update(json.dumps(self.metadata[key], sort_keys=True).encode())
        
        return h.hexdigest()
    
    def export(self) -> Dict[str, Any]:
        """
        Exporta artefato completo
        
        Returns:
            Dicionário com estrutura completa do artefato
        """
        if not self.finalized:
            raise RuntimeError("Artefato deve ser finalizado antes de exportar")
        
        return {
            "genesis_hash": self.genesis_hash,
            "version": "1.0.0",
            "protocol": "CORE_B_DAY",
            
            # Vetor de integridade
            "integrity_vector": {
                "bundle_hash": self.bundle.compute_bundle_hash(),
                "manifest": self.bundle.get_manifest(),
                "file_count": len(self.bundle.files)
            },
            
            # Compromisso de identidade
            "identity_commitment": {
                "puf_id": self.puf_id,
                "ohash": self.ohash,
                "entropy_bits": self.entropy_bits
            },
            
            # Hash do testemunho físico
            "physical_witness": {
                "puf_id": self.puf_id,
                "entropy_bits": self.entropy_bits
            },
            
            # Âncoras temporais
            "temporal_anchors": self.triple_anchor.export(),
            
            # Experimento
            "experiment": {
                "name": self.experiment_name,
                "description": self.experiment_description,
                "metadata": self.metadata
            },
            
            # Assinaturas
            "signatures": self.signatures,
            
            # Política de linhagem
            "lineage_policy": {
                "parent": None,  # Genesis não tem pai
                "fork_allowed": True,
                "fork_policy": "open"
            }
        }
    
    def save_to_file(self, filepath: str) -> None:
        """
        Salva artefato em arquivo JSON
        
        Args:
            filepath: Caminho do arquivo
        """
        if not self.finalized:
            raise RuntimeError("Artefato deve ser finalizado antes de salvar")
        
        with open(filepath, 'w') as f:
            json.dump(self.export(), f, indent=2)
    
    def verify(self) -> bool:
        """
        Verifica integridade do artefato
        
        Returns:
            True se íntegro
        """
        if not self.finalized:
            return False
        
        # Recomputa genesis hash
        recomputed_hash = self._compute_genesis_hash()
        
        # Verifica se corresponde
        if recomputed_hash != self.genesis_hash:
            return False
        
        # Verifica consistência das âncoras
        if not self.triple_anchor.verify_consistency():
            return False
        
        return True
    
    def __repr__(self) -> str:
        status = "finalized" if self.finalized else "draft"
        return (
            f"GenesisArtifact("
            f"name={self.experiment_name}, "
            f"ohash={self.ohash[:16]}..., "
            f"status={status})"
        )
