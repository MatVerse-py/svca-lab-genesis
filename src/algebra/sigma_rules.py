"""
Σ-Rules (Sigma Rules) - Regras de estados proibidos

Define transições impossíveis e estados que violam leis físicas
ou lógicas do sistema.

Exemplos:
- Timestamp retroativo
- Localização fisicamente impossível
- Temperatura fora de limites físicos
- Hash de estado anterior inválido
"""

from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class RuleSeverity(Enum):
    """Severidade da violação de regra"""
    CRITICAL = "critical"  # Bloqueia imediatamente
    ERROR = "error"        # Bloqueia mas permite override em casos especiais
    WARNING = "warning"    # Registra mas não bloqueia


@dataclass
class RuleViolation:
    """Registro de violação de regra"""
    
    rule_id: str
    """ID da regra violada"""
    
    severity: RuleSeverity
    """Severidade da violação"""
    
    message: str
    """Mensagem descritiva"""
    
    state: Dict[str, Any]
    """Estado que causou violação"""
    
    def __repr__(self) -> str:
        return f"RuleViolation({self.rule_id}: {self.message})"


class SigmaRule:
    """
    Regra Σ individual
    
    Define condição que, se violada, indica estado impossível.
    """
    
    def __init__(
        self,
        rule_id: str,
        description: str,
        validator: Callable[[Dict[str, Any]], bool],
        severity: RuleSeverity = RuleSeverity.CRITICAL
    ):
        """
        Inicializa regra Σ
        
        Args:
            rule_id: Identificador único da regra
            description: Descrição da regra
            validator: Função que retorna True se estado é válido
            severity: Severidade da violação
        """
        self.rule_id = rule_id
        self.description = description
        self.validator = validator
        self.severity = severity
    
    def check(self, state: Dict[str, Any]) -> Optional[RuleViolation]:
        """
        Verifica se estado viola regra
        
        Args:
            state: Estado a verificar
        
        Returns:
            RuleViolation se violado, None caso contrário
        """
        try:
            is_valid = self.validator(state)
            
            if not is_valid:
                return RuleViolation(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    message=f"Violação: {self.description}",
                    state=state
                )
            
            return None
        
        except Exception as e:
            # Erro na validação = estado suspeito
            return RuleViolation(
                rule_id=self.rule_id,
                severity=RuleSeverity.CRITICAL,
                message=f"Erro ao validar: {str(e)}",
                state=state
            )
    
    def __repr__(self) -> str:
        return f"SigmaRule({self.rule_id}: {self.description})"


class SigmaRuleSet:
    """
    Conjunto de regras Σ
    
    Gerencia múltiplas regras e valida estados contra todas elas.
    """
    
    def __init__(self):
        """Inicializa conjunto vazio de regras"""
        self.rules: Dict[str, SigmaRule] = {}
    
    def add_rule(self, rule: SigmaRule) -> None:
        """
        Adiciona regra ao conjunto
        
        Args:
            rule: Regra a adicionar
        """
        if rule.rule_id in self.rules:
            raise ValueError(f"Regra {rule.rule_id} já existe")
        
        self.rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str) -> None:
        """
        Remove regra do conjunto
        
        Args:
            rule_id: ID da regra a remover
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    def check_all(self, state: Dict[str, Any]) -> List[RuleViolation]:
        """
        Verifica estado contra todas as regras
        
        Args:
            state: Estado a verificar
        
        Returns:
            Lista de violações (vazia se estado é válido)
        """
        violations = []
        
        for rule in self.rules.values():
            violation = rule.check(state)
            if violation is not None:
                violations.append(violation)
        
        return violations
    
    def is_valid(self, state: Dict[str, Any]) -> bool:
        """
        Verifica se estado é válido (sem violações críticas)
        
        Args:
            state: Estado a verificar
        
        Returns:
            True se válido
        """
        violations = self.check_all(state)
        
        # Bloqueia se houver violações críticas
        critical_violations = [
            v for v in violations
            if v.severity == RuleSeverity.CRITICAL
        ]
        
        return len(critical_violations) == 0
    
    def get_rule(self, rule_id: str) -> Optional[SigmaRule]:
        """
        Busca regra por ID
        
        Args:
            rule_id: ID da regra
        
        Returns:
            Regra se encontrada
        """
        return self.rules.get(rule_id)
    
    def count(self) -> int:
        """Retorna número de regras"""
        return len(self.rules)
    
    def __repr__(self) -> str:
        return f"SigmaRuleSet(rules={len(self.rules)})"


# Regras Σ padrão do CORE B DAY

def create_default_rules() -> SigmaRuleSet:
    """
    Cria conjunto de regras Σ padrão
    
    Returns:
        SigmaRuleSet com regras fundamentais
    """
    ruleset = SigmaRuleSet()
    
    # Regra 1: Timestamp não pode ser retroativo
    ruleset.add_rule(SigmaRule(
        rule_id="SIGMA_001_TIMESTAMP_MONOTONIC",
        description="Timestamp deve ser monotonicamente crescente",
        validator=lambda state: (
            "timestamp" not in state or
            "prev_timestamp" not in state or
            state["timestamp"] >= state["prev_timestamp"]
        ),
        severity=RuleSeverity.CRITICAL
    ))
    
    # Regra 2: Hash anterior deve ser válido
    ruleset.add_rule(SigmaRule(
        rule_id="SIGMA_002_PREV_HASH_VALID",
        description="Hash de estado anterior deve ser válido",
        validator=lambda state: (
            "prev_hash" not in state or
            (isinstance(state["prev_hash"], str) and len(state["prev_hash"]) == 64)
        ),
        severity=RuleSeverity.CRITICAL
    ))
    
    # Regra 3: Temperatura deve estar em limites físicos
    ruleset.add_rule(SigmaRule(
        rule_id="SIGMA_003_TEMPERATURE_PHYSICAL",
        description="Temperatura deve estar em limites físicos (-273.15°C a 5000°C)",
        validator=lambda state: (
            "temperature" not in state or
            (-273.15 <= state["temperature"] <= 5000.0)
        ),
        severity=RuleSeverity.CRITICAL
    ))
    
    # Regra 4: Localização deve ser válida
    ruleset.add_rule(SigmaRule(
        rule_id="SIGMA_004_LOCATION_VALID",
        description="Localização deve ter latitude [-90, 90] e longitude [-180, 180]",
        validator=lambda state: (
            "location" not in state or
            (
                isinstance(state["location"], (tuple, list)) and
                len(state["location"]) == 2 and
                -90 <= state["location"][0] <= 90 and
                -180 <= state["location"][1] <= 180
            )
        ),
        severity=RuleSeverity.CRITICAL
    ))
    
    # Regra 5: Entropia mínima
    ruleset.add_rule(SigmaRule(
        rule_id="SIGMA_005_ENTROPY_MINIMUM",
        description="Entropia deve ser >= 128 bits (requisito CORE B DAY)",
        validator=lambda state: (
            "entropy_bits" not in state or
            state["entropy_bits"] >= 128.0
        ),
        severity=RuleSeverity.CRITICAL
    ))
    
    # Regra 6: PUF ID deve existir
    ruleset.add_rule(SigmaRule(
        rule_id="SIGMA_006_PUF_ID_EXISTS",
        description="PUF ID deve estar presente e não vazio",
        validator=lambda state: (
            "puf_id" not in state or
            (isinstance(state["puf_id"], str) and len(state["puf_id"]) > 0)
        ),
        severity=RuleSeverity.CRITICAL
    ))
    
    # Regra 7: BER deve estar em limites aceitáveis
    ruleset.add_rule(SigmaRule(
        rule_id="SIGMA_007_BER_ACCEPTABLE",
        description="BER (Bit Error Rate) deve estar entre 0.0 e 0.5",
        validator=lambda state: (
            "ber" not in state or
            (0.0 <= state["ber"] <= 0.5)
        ),
        severity=RuleSeverity.ERROR
    ))
    
    # Regra 8: Velocidade de movimento fisicamente possível
    ruleset.add_rule(SigmaRule(
        rule_id="SIGMA_008_VELOCITY_PHYSICAL",
        description="Velocidade de movimento deve ser fisicamente possível",
        validator=lambda state: (
            "prev_location" not in state or
            "location" not in state or
            "timestamp" not in state or
            "prev_timestamp" not in state or
            _check_velocity_physical(state)
        ),
        severity=RuleSeverity.CRITICAL
    ))
    
    return ruleset


def _check_velocity_physical(state: Dict[str, Any]) -> bool:
    """
    Verifica se velocidade de movimento é fisicamente possível
    
    Calcula distância entre localizações e tempo decorrido.
    Velocidade máxima: ~300 m/s (velocidade do som + margem)
    
    Args:
        state: Estado com prev_location, location, prev_timestamp, timestamp
    
    Returns:
        True se velocidade é possível
    """
    try:
        from math import radians, sin, cos, sqrt, atan2
        
        # Extrai dados
        lat1, lon1 = state["prev_location"]
        lat2, lon2 = state["location"]
        t1 = state["prev_timestamp"]
        t2 = state["timestamp"]
        
        # Calcula distância (fórmula de Haversine)
        R = 6371000  # Raio da Terra em metros
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        # Calcula tempo decorrido (assume timestamps em segundos)
        time_elapsed = t2 - t1
        
        if time_elapsed <= 0:
            return False
        
        # Calcula velocidade
        velocity = distance / time_elapsed
        
        # Velocidade máxima: 500 m/s (margem para aviões supersônicos)
        max_velocity = 500.0
        
        return velocity <= max_velocity
    
    except Exception:
        # Em caso de erro, assume válido (fail-open neste caso específico)
        return True
