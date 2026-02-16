"""
Ψ-State (Psi State) - Estado atual do sistema

Representa o estado atual do sistema na álgebra de possibilidades.

Vetor de estado CORE B DAY:
S(t) = F(P, T, L, Θ, E, H, Ψ ...)

Onde:
- P: PUF (raiz física)
- T: Timestamp
- L: Localização
- Θ: Temperatura
- E: Entropia
- H: Hash anterior
- Ψ: Estado algébrico
"""

import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StateVector:
    """
    Vetor de estado S(t)
    
    Representa snapshot completo do sistema em um instante.
    """
    
    # Componentes obrigatórios
    puf_id: str
    """P: Identidade do PUF (raiz física)"""
    
    timestamp: float
    """T: Timestamp Unix"""
    
    # Componentes opcionais
    location: Optional[tuple[float, float]] = None
    """L: Localização (latitude, longitude)"""
    
    temperature: Optional[float] = None
    """Θ: Temperatura em Celsius"""
    
    entropy_bits: Optional[float] = None
    """E: Entropia em bits"""
    
    prev_hash: Optional[str] = None
    """H: Hash do estado anterior"""
    
    psi_state_id: Optional[str] = None
    """Ψ: ID do estado algébrico"""
    
    # Metadados adicionais
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Metadados adicionais"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "puf_id": self.puf_id,
            "timestamp": self.timestamp,
            "location": self.location,
            "temperature": self.temperature,
            "entropy_bits": self.entropy_bits,
            "prev_hash": self.prev_hash,
            "psi_state_id": self.psi_state_id,
            "metadata": self.metadata
        }
    
    def compute_hash(self) -> str:
        """
        Computa hash do vetor de estado
        
        Returns:
            Hash SHA3-256 do estado
        """
        h = hashlib.sha3_256()
        
        # Serializa componentes em ordem determinística
        h.update(b"STATE_VECTOR")
        h.update(self.puf_id.encode())
        h.update(str(self.timestamp).encode())
        
        if self.location is not None:
            h.update(str(self.location).encode())
        
        if self.temperature is not None:
            h.update(str(self.temperature).encode())
        
        if self.entropy_bits is not None:
            h.update(str(self.entropy_bits).encode())
        
        if self.prev_hash is not None:
            h.update(self.prev_hash.encode())
        
        if self.psi_state_id is not None:
            h.update(self.psi_state_id.encode())
        
        return h.hexdigest()
    
    def __repr__(self) -> str:
        return f"StateVector(puf={self.puf_id[:8]}..., t={self.timestamp})"


class PsiState:
    """
    Estado Ψ do sistema
    
    Mantém histórico de estados e permite navegação na trajetória.
    
    Propriedades:
    - Append-only: Estados não podem ser removidos
    - Ordenado: Estados mantêm ordem temporal
    - Verificável: Cada estado referencia anterior via hash
    """
    
    def __init__(self, genesis_vector: Optional[StateVector] = None):
        """
        Inicializa estado Ψ
        
        Args:
            genesis_vector: Vetor de estado inicial (Genesis)
        """
        self.states: list[StateVector] = []
        self.state_hashes: list[str] = []
        
        if genesis_vector is not None:
            self.append(genesis_vector)
    
    def append(self, vector: StateVector) -> str:
        """
        Adiciona novo estado à trajetória
        
        Args:
            vector: Vetor de estado a adicionar
        
        Returns:
            Hash do estado adicionado
        """
        # Se não é o primeiro estado, atualiza prev_hash
        if len(self.states) > 0:
            vector.prev_hash = self.state_hashes[-1]
        
        # Atualiza psi_state_id
        vector.psi_state_id = f"PSI_{len(self.states)}"
        
        # Computa hash
        state_hash = vector.compute_hash()
        
        # Adiciona à trajetória
        self.states.append(vector)
        self.state_hashes.append(state_hash)
        
        return state_hash
    
    def get_current(self) -> Optional[StateVector]:
        """
        Retorna estado atual (último)
        
        Returns:
            Estado atual ou None se vazio
        """
        if len(self.states) == 0:
            return None
        return self.states[-1]
    
    def get_by_index(self, index: int) -> Optional[StateVector]:
        """
        Retorna estado por índice
        
        Args:
            index: Índice do estado (0 = Genesis)
        
        Returns:
            Estado ou None se índice inválido
        """
        if 0 <= index < len(self.states):
            return self.states[index]
        return None
    
    def get_by_hash(self, state_hash: str) -> Optional[StateVector]:
        """
        Retorna estado por hash
        
        Args:
            state_hash: Hash do estado
        
        Returns:
            Estado ou None se não encontrado
        """
        try:
            index = self.state_hashes.index(state_hash)
            return self.states[index]
        except ValueError:
            return None
    
    def get_genesis(self) -> Optional[StateVector]:
        """
        Retorna estado Genesis (primeiro)
        
        Returns:
            Estado Genesis ou None se vazio
        """
        if len(self.states) == 0:
            return None
        return self.states[0]
    
    def verify_chain(self) -> bool:
        """
        Verifica integridade da cadeia de estados
        
        Valida que cada estado referencia corretamente o anterior.
        
        Returns:
            True se cadeia é válida
        """
        for i in range(1, len(self.states)):
            current = self.states[i]
            prev_hash = self.state_hashes[i-1]
            
            if current.prev_hash != prev_hash:
                return False
        
        return True
    
    def get_trajectory(self) -> list[StateVector]:
        """
        Retorna trajetória completa
        
        Returns:
            Lista de todos os estados em ordem
        """
        return self.states.copy()
    
    def count(self) -> int:
        """
        Retorna número de estados
        
        Returns:
            Número de estados na trajetória
        """
        return len(self.states)
    
    def compute_trajectory_hash(self) -> str:
        """
        Computa hash da trajetória completa
        
        Returns:
            Hash SHA3-256 de todos os estados
        """
        h = hashlib.sha3_256()
        h.update(b"TRAJECTORY")
        
        for state_hash in self.state_hashes:
            h.update(state_hash.encode())
        
        return h.hexdigest()
    
    def export_trajectory(self) -> Dict[str, Any]:
        """
        Exporta trajetória para formato serializável
        
        Returns:
            Dicionário com trajetória completa
        """
        return {
            "genesis_hash": self.state_hashes[0] if len(self.state_hashes) > 0 else None,
            "current_hash": self.state_hashes[-1] if len(self.state_hashes) > 0 else None,
            "trajectory_hash": self.compute_trajectory_hash(),
            "state_count": len(self.states),
            "states": [s.to_dict() for s in self.states],
            "hashes": self.state_hashes
        }
    
    def __repr__(self) -> str:
        return f"PsiState(states={len(self.states)}, valid={self.verify_chain()})"
    
    def __len__(self) -> int:
        return len(self.states)
