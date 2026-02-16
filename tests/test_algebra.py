"""
Testes para módulo de álgebra Σ-Ω-Ψ
"""

import pytest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from algebra.sigma_rules import SigmaRule, SigmaRuleSet, RuleSeverity, create_default_rules
from algebra.psi_state import PsiState, StateVector
from algebra.omega_gate import OmegaGate, GateDecision


class TestSigmaRules:
    """Testes para Σ-Rules"""
    
    def test_rule_creation(self):
        """Testa criação de regra"""
        rule = SigmaRule(
            rule_id="TEST_001",
            description="Teste",
            validator=lambda state: True,
            severity=RuleSeverity.CRITICAL
        )
        
        assert rule.rule_id == "TEST_001"
        assert rule.severity == RuleSeverity.CRITICAL
    
    def test_rule_validation_pass(self):
        """Testa validação que passa"""
        rule = SigmaRule(
            rule_id="TEST_POSITIVE",
            description="Valor deve ser positivo",
            validator=lambda state: state.get("value", 0) > 0
        )
        
        violation = rule.check({"value": 10})
        assert violation is None
    
    def test_rule_validation_fail(self):
        """Testa validação que falha"""
        rule = SigmaRule(
            rule_id="TEST_POSITIVE",
            description="Valor deve ser positivo",
            validator=lambda state: state.get("value", 0) > 0
        )
        
        violation = rule.check({"value": -5})
        assert violation is not None
        assert violation.rule_id == "TEST_POSITIVE"
    
    def test_ruleset(self):
        """Testa conjunto de regras"""
        ruleset = SigmaRuleSet()
        
        ruleset.add_rule(SigmaRule(
            rule_id="R1",
            description="R1",
            validator=lambda s: s.get("a", 0) > 0
        ))
        
        ruleset.add_rule(SigmaRule(
            rule_id="R2",
            description="R2",
            validator=lambda s: s.get("b", 0) > 0
        ))
        
        assert ruleset.count() == 2
        
        # Estado válido
        assert ruleset.is_valid({"a": 1, "b": 1})
        
        # Estado inválido
        assert not ruleset.is_valid({"a": -1, "b": 1})
    
    def test_default_rules(self):
        """Testa regras padrão do CORE B DAY"""
        ruleset = create_default_rules()
        
        # Deve ter regras fundamentais
        assert ruleset.count() >= 5
        
        # Testa regra de entropia mínima
        assert ruleset.is_valid({"entropy_bits": 256.0})
        assert not ruleset.is_valid({"entropy_bits": 64.0})  # Abaixo de 128
        
        # Testa regra de timestamp monotônico
        assert ruleset.is_valid({
            "timestamp": 100,
            "prev_timestamp": 50
        })
        assert not ruleset.is_valid({
            "timestamp": 50,
            "prev_timestamp": 100
        })


class TestPsiState:
    """Testes para Ψ-State"""
    
    def test_creation(self):
        """Testa criação de Ψ-State"""
        genesis = StateVector(
            puf_id="test_puf",
            timestamp=time.time()
        )
        
        psi = PsiState(genesis_vector=genesis)
        assert psi.count() == 1
        assert psi.get_genesis() == genesis
    
    def test_append(self):
        """Testa adição de estados"""
        genesis = StateVector(puf_id="test", timestamp=1.0)
        psi = PsiState(genesis_vector=genesis)
        
        # Adiciona novo estado
        state2 = StateVector(puf_id="test", timestamp=2.0)
        hash2 = psi.append(state2)
        
        assert psi.count() == 2
        assert len(hash2) == 64  # SHA3-256
    
    def test_chain_verification(self):
        """Testa verificação de cadeia"""
        genesis = StateVector(puf_id="test", timestamp=1.0)
        psi = PsiState(genesis_vector=genesis)
        
        # Adiciona estados
        for i in range(5):
            state = StateVector(puf_id="test", timestamp=float(i+2))
            psi.append(state)
        
        # Cadeia deve ser válida
        assert psi.verify_chain()
        assert psi.count() == 6
    
    def test_trajectory(self):
        """Testa obtenção de trajetória"""
        genesis = StateVector(puf_id="test", timestamp=1.0)
        psi = PsiState(genesis_vector=genesis)
        
        for i in range(3):
            psi.append(StateVector(puf_id="test", timestamp=float(i+2)))
        
        trajectory = psi.get_trajectory()
        assert len(trajectory) == 4
        assert trajectory[0] == genesis


class TestOmegaGate:
    """Testes para Ω-Gate"""
    
    def test_creation(self):
        """Testa criação de Ω-Gate"""
        ruleset = create_default_rules()
        gate = OmegaGate(sigma_rules=ruleset, strict_mode=True)
        
        assert gate.strict_mode is True
    
    def test_block_invalid_signature(self):
        """Testa bloqueio de assinatura inválida"""
        ruleset = create_default_rules()
        gate = OmegaGate(sigma_rules=ruleset)
        
        genesis = StateVector(puf_id="test", timestamp=time.time(), entropy_bits=256.0)
        psi = PsiState(genesis_vector=genesis)
        
        new_state = StateVector(puf_id="test", timestamp=time.time(), entropy_bits=256.0)
        
        # Sem assinatura válida
        result = gate.validate(new_state, psi, signature_valid=False)
        
        assert result.decision == GateDecision.BLOCK
        assert not result.signature_valid
    
    def test_allow_valid_transition(self):
        """Testa permissão de transição válida"""
        ruleset = create_default_rules()
        gate = OmegaGate(sigma_rules=ruleset, strict_mode=False)
        
        genesis = StateVector(
            puf_id="test",
            timestamp=time.time(),
            entropy_bits=256.0,
            location=(0.0, 0.0),
            temperature=20.0
        )
        psi = PsiState(genesis_vector=genesis)
        
        time.sleep(0.01)  # Pequeno delay
        
        new_state = StateVector(
            puf_id="test",
            timestamp=time.time(),
            entropy_bits=256.0,
            location=(0.0, 0.0),
            temperature=20.5
        )
        
        result = gate.validate(new_state, psi, signature_valid=True)
        
        assert result.decision == GateDecision.ALLOW
        assert result.signature_valid
        assert result.trajectory_valid
    
    def test_block_retroactive_timestamp(self):
        """Testa bloqueio de timestamp retroativo"""
        ruleset = create_default_rules()
        gate = OmegaGate(sigma_rules=ruleset)
        
        genesis = StateVector(puf_id="test", timestamp=100.0, entropy_bits=256.0)
        psi = PsiState(genesis_vector=genesis)
        
        # Timestamp retroativo
        invalid_state = StateVector(puf_id="test", timestamp=50.0, entropy_bits=256.0)
        
        result = gate.validate(invalid_state, psi, signature_valid=True)
        
        assert result.decision == GateDecision.BLOCK
        assert len(result.violations) > 0
    
    def test_block_low_entropy(self):
        """Testa bloqueio de entropia baixa"""
        ruleset = create_default_rules()
        gate = OmegaGate(sigma_rules=ruleset)
        
        genesis = StateVector(puf_id="test", timestamp=1.0, entropy_bits=256.0)
        psi = PsiState(genesis_vector=genesis)
        
        # Entropia abaixo do mínimo (128 bits)
        invalid_state = StateVector(puf_id="test", timestamp=2.0, entropy_bits=64.0)
        
        result = gate.validate(invalid_state, psi, signature_valid=True)
        
        assert result.decision == GateDecision.BLOCK
    
    def test_statistics(self):
        """Testa estatísticas do gate"""
        ruleset = create_default_rules()
        gate = OmegaGate(sigma_rules=ruleset, strict_mode=False)
        
        genesis = StateVector(puf_id="test", timestamp=1.0, entropy_bits=256.0)
        psi = PsiState(genesis_vector=genesis)
        
        # Valida alguns estados
        for i in range(5):
            state = StateVector(puf_id="test", timestamp=float(i+2), entropy_bits=256.0)
            gate.validate(state, psi, signature_valid=True)
        
        stats = gate.get_statistics()
        assert stats["total"] == 5
        assert stats["allowed"] + stats["blocked"] == 5


def test_fail_closed_principle():
    """Testa princípio fail-closed absoluto"""
    ruleset = create_default_rules()
    gate = OmegaGate(sigma_rules=ruleset, strict_mode=True)
    
    genesis = StateVector(puf_id="test", timestamp=1.0, entropy_bits=256.0)
    psi = PsiState(genesis_vector=genesis)
    
    # Casos que devem ser bloqueados
    invalid_cases = [
        # Sem assinatura
        (StateVector(puf_id="test", timestamp=2.0, entropy_bits=256.0), False),
        # Timestamp retroativo
        (StateVector(puf_id="test", timestamp=0.5, entropy_bits=256.0), True),
        # Entropia baixa
        (StateVector(puf_id="test", timestamp=2.0, entropy_bits=50.0), True),
    ]
    
    for state, sig_valid in invalid_cases:
        result = gate.validate(state, psi, signature_valid=sig_valid)
        assert result.decision == GateDecision.BLOCK, \
            f"Deveria bloquear: {state}, sig_valid={sig_valid}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
