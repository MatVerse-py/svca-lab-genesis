"""
Álgebra Σ-Ω-Ψ Module

Implementa sistema de filtros de realidade que valida trajetórias
e bloqueia estados impossíveis, mesmo com assinatura válida.

Componentes:
- Σ-Rules: Regras que definem estados proibidos
- Ω-Gate: Portão de admissibilidade que valida trajetórias
- Ψ-State: Estado atual do sistema na álgebra de possibilidades

Propriedade fundamental CORE B DAY:
Assinatura correta ≠ transação válida
"""

from .sigma_rules import SigmaRule, SigmaRuleSet
from .omega_gate import OmegaGate, GateDecision
from .psi_state import PsiState, StateVector

__all__ = [
    "SigmaRule",
    "SigmaRuleSet",
    "OmegaGate",
    "GateDecision",
    "PsiState",
    "StateVector",
]
