"""
Genesis Module - Sistema de artefato Genesis

Implementa evento irreversível que torna origem externamente verificável.

Estrutura do artefato Genesis (CORE B DAY):
- Vetor de integridade
- Compromisso de identidade
- Hashes do bundle
- Hash do testemunho físico
- Assinaturas
- Âncoras temporais (triple anchor)
- Política de linhagem

Resultado: "Together these elements form a closed verification loop."
"""

from .genesis_artifact import GenesisArtifact, GenesisBundle
from .triple_anchor import TripleAnchor, AnchorType

__all__ = [
    "GenesisArtifact",
    "GenesisBundle",
    "TripleAnchor",
    "AnchorType",
]
