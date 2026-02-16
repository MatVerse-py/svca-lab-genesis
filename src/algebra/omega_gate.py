"""
Ω-Gate (Omega Gate) - Portão de admissibilidade

Valida trajetórias e decide se transição de estado é permitida.

Propriedade fundamental CORE B DAY:
Assinatura correta ≠ transação válida

Mesmo com assinatura criptográfica válida, a transição é bloqueada
se a trajetória for impossível segundo as regras Σ.
"""

from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
from .sigma_rules import SigmaRuleSet, RuleViolation, RuleSeverity
from .psi_state import PsiState, StateVector


class GateDecision(Enum):
    """Decisão do Ω-Gate"""
    ALLOW = "allow"      # Permite transição
    BLOCK = "block"      # Bloqueia transição
    QUARANTINE = "quarantine"  # Quarentena para análise


@dataclass
class GateResult:
    """
    Resultado da validação do Ω-Gate
    """
    
    decision: GateDecision
    """Decisão final"""
    
    violations: List[RuleViolation]
    """Lista de violações detectadas"""
    
    message: str
    """Mensagem explicativa"""
    
    state_vector: StateVector
    """Vetor de estado avaliado"""
    
    signature_valid: bool = False
    """Se assinatura criptográfica é válida"""
    
    trajectory_valid: bool = False
    """Se trajetória é válida"""
    
    def is_allowed(self) -> bool:
        """Retorna True se transição é permitida"""
        return self.decision == GateDecision.ALLOW
    
    def __repr__(self) -> str:
        return f"GateResult({self.decision.value}: {self.message})"


class OmegaGate:
    """
    Ω-Gate: Portão de admissibilidade
    
    Implementa fail-closed absoluto:
    - Assinatura inválida → BLOCK
    - Violação de regra Σ → BLOCK
    - Trajetória impossível → BLOCK
    - Qualquer dúvida → BLOCK
    
    Nunca deixa passar em caso de incerteza.
    """
    
    def __init__(
        self,
        sigma_rules: SigmaRuleSet,
        strict_mode: bool = True
    ):
        """
        Inicializa Ω-Gate
        
        Args:
            sigma_rules: Conjunto de regras Σ
            strict_mode: Se True, bloqueia em qualquer violação (mesmo WARNING)
        """
        self.sigma_rules = sigma_rules
        self.strict_mode = strict_mode
        self.blocked_count = 0
        self.allowed_count = 0
    
    def validate(
        self,
        state_vector: StateVector,
        psi_state: PsiState,
        signature_valid: bool = False
    ) -> GateResult:
        """
        Valida transição de estado
        
        Args:
            state_vector: Novo vetor de estado proposto
            psi_state: Estado Ψ atual do sistema
            signature_valid: Se assinatura criptográfica é válida
        
        Returns:
            GateResult com decisão e detalhes
        """
        # 1. Verifica assinatura criptográfica
        if not signature_valid:
            self.blocked_count += 1
            return GateResult(
                decision=GateDecision.BLOCK,
                violations=[],
                message="Assinatura criptográfica inválida",
                state_vector=state_vector,
                signature_valid=False,
                trajectory_valid=False
            )
        
        # 2. Prepara estado completo para validação
        current_state = psi_state.get_current()
        
        validation_state = state_vector.to_dict()
        
        # Adiciona informações do estado anterior se existir
        if current_state is not None:
            validation_state["prev_timestamp"] = current_state.timestamp
            validation_state["prev_location"] = current_state.location
            validation_state["prev_hash"] = psi_state.state_hashes[-1]
        
        # 3. Valida contra regras Σ
        violations = self.sigma_rules.check_all(validation_state)
        
        # 4. Decide baseado em violações
        critical_violations = [
            v for v in violations
            if v.severity == RuleSeverity.CRITICAL
        ]
        
        error_violations = [
            v for v in violations
            if v.severity == RuleSeverity.ERROR
        ]
        
        warning_violations = [
            v for v in violations
            if v.severity == RuleSeverity.WARNING
        ]
        
        # 5. Fail-closed: bloqueia se houver violações críticas
        if len(critical_violations) > 0:
            self.blocked_count += 1
            return GateResult(
                decision=GateDecision.BLOCK,
                violations=violations,
                message=f"Violações críticas detectadas: {len(critical_violations)}",
                state_vector=state_vector,
                signature_valid=True,
                trajectory_valid=False
            )
        
        # 6. Modo strict: bloqueia em qualquer violação
        if self.strict_mode and (len(error_violations) > 0 or len(warning_violations) > 0):
            self.blocked_count += 1
            return GateResult(
                decision=GateDecision.BLOCK,
                violations=violations,
                message=f"Modo strict: {len(violations)} violações detectadas",
                state_vector=state_vector,
                signature_valid=True,
                trajectory_valid=False
            )
        
        # 7. Quarentena se houver erros (mas não críticos)
        if len(error_violations) > 0:
            return GateResult(
                decision=GateDecision.QUARANTINE,
                violations=violations,
                message=f"Erros detectados: {len(error_violations)} (quarentena)",
                state_vector=state_vector,
                signature_valid=True,
                trajectory_valid=False
            )
        
        # 8. Permite transição
        self.allowed_count += 1
        return GateResult(
            decision=GateDecision.ALLOW,
            violations=violations,  # Pode ter warnings
            message="Transição permitida",
            state_vector=state_vector,
            signature_valid=True,
            trajectory_valid=True
        )
    
    def validate_and_append(
        self,
        state_vector: StateVector,
        psi_state: PsiState,
        signature_valid: bool = False
    ) -> GateResult:
        """
        Valida e, se permitido, adiciona estado ao Ψ
        
        Args:
            state_vector: Novo vetor de estado
            psi_state: Estado Ψ atual
            signature_valid: Se assinatura é válida
        
        Returns:
            GateResult com decisão
        """
        result = self.validate(state_vector, psi_state, signature_valid)
        
        # Só adiciona se permitido
        if result.is_allowed():
            psi_state.append(state_vector)
        
        return result
    
    def get_statistics(self) -> dict:
        """
        Retorna estatísticas do gate
        
        Returns:
            Dicionário com contadores
        """
        total = self.allowed_count + self.blocked_count
        
        return {
            "allowed": self.allowed_count,
            "blocked": self.blocked_count,
            "total": total,
            "block_rate": self.blocked_count / total if total > 0 else 0.0,
            "strict_mode": self.strict_mode
        }
    
    def reset_statistics(self) -> None:
        """Reseta contadores"""
        self.allowed_count = 0
        self.blocked_count = 0
    
    def __repr__(self) -> str:
        stats = self.get_statistics()
        return (
            f"OmegaGate("
            f"rules={self.sigma_rules.count()}, "
            f"strict={self.strict_mode}, "
            f"blocked={stats['blocked']}/{stats['total']})"
        )


class AntiFragilityMetrics:
    """
    Métricas de antifragilidade αᵣ
    
    Mede ganho de entropia após ataques:
    αᵣ = (H_after − H_before) / E_attack
    
    Requisito CORE B DAY: αᵣ ≥ 1
    """
    
    def __init__(self):
        """Inicializa métricas"""
        self.attack_events: List[dict] = []
    
    def record_attack(
        self,
        entropy_before: float,
        entropy_after: float,
        attack_energy: float
    ) -> float:
        """
        Registra evento de ataque e calcula αᵣ
        
        Args:
            entropy_before: Entropia antes do ataque
            entropy_after: Entropia depois do ataque
            attack_energy: Energia do ataque (custo)
        
        Returns:
            Valor de αᵣ para este ataque
        """
        if attack_energy <= 0:
            return 0.0
        
        alpha_r = (entropy_after - entropy_before) / attack_energy
        
        self.attack_events.append({
            "entropy_before": entropy_before,
            "entropy_after": entropy_after,
            "attack_energy": attack_energy,
            "alpha_r": alpha_r,
            "antifragile": alpha_r >= 1.0
        })
        
        return alpha_r
    
    def is_antifragile(self) -> bool:
        """
        Verifica se sistema é antifrágil
        
        Returns:
            True se αᵣ médio ≥ 1
        """
        if len(self.attack_events) == 0:
            return True  # Sem ataques = assume antifrágil
        
        avg_alpha = sum(e["alpha_r"] for e in self.attack_events) / len(self.attack_events)
        return avg_alpha >= 1.0
    
    def get_average_alpha(self) -> float:
        """
        Retorna αᵣ médio
        
        Returns:
            Média de αᵣ
        """
        if len(self.attack_events) == 0:
            return 1.0
        
        return sum(e["alpha_r"] for e in self.attack_events) / len(self.attack_events)
    
    def __repr__(self) -> str:
        return (
            f"AntiFragilityMetrics("
            f"attacks={len(self.attack_events)}, "
            f"avg_alpha={self.get_average_alpha():.2f}, "
            f"antifragile={self.is_antifragile()})"
        )
