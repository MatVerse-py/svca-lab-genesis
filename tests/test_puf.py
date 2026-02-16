"""
Testes para módulo PUF
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from puf.simulated_puf import SimulatedPUF
from puf.optical_puf import OpticalPUF
from puf.sram_puf import SRAMPUF


class TestSimulatedPUF:
    """Testes para SimulatedPUF"""
    
    def test_creation(self):
        """Testa criação de PUF"""
        puf = SimulatedPUF(seed=42)
        assert puf.get_id() is not None
        assert len(puf.get_id()) > 0
    
    def test_entropy(self):
        """Testa entropia mínima"""
        puf = SimulatedPUF(seed=42, entropy_bits=256.0)
        assert puf.get_entropy() >= 128.0  # Requisito CORE B DAY
    
    def test_ber(self):
        """Testa BER em limites aceitáveis"""
        puf = SimulatedPUF(seed=42, ber=0.02)
        assert 0.0 <= puf.get_ber() <= 0.5
    
    def test_generate(self):
        """Testa geração de resposta"""
        puf = SimulatedPUF(seed=42)
        response = puf.generate()
        
        assert response.response is not None
        assert len(response.response) > 0
        assert response.entropy_bits > 0
        assert 0.0 <= response.bit_error_rate <= 0.5
    
    def test_determinism(self):
        """Testa determinismo com mesma seed"""
        puf1 = SimulatedPUF(seed=42)
        puf2 = SimulatedPUF(seed=42)
        
        # IDs devem ser iguais
        assert puf1.get_id() == puf2.get_id()
        
        # Respostas estáveis devem ser iguais
        resp1 = puf1.get_stable_response()
        resp2 = puf2.get_stable_response()
        assert resp1 == resp2
    
    def test_uniqueness(self):
        """Testa unicidade com seeds diferentes"""
        puf1 = SimulatedPUF(seed=42)
        puf2 = SimulatedPUF(seed=43)
        
        # IDs devem ser diferentes
        assert puf1.get_id() != puf2.get_id()
        
        # Respostas devem ser diferentes
        resp1 = puf1.get_stable_response()
        resp2 = puf2.get_stable_response()
        assert resp1 != resp2


class TestOpticalPUF:
    """Testes para OpticalPUF"""
    
    def test_creation(self):
        """Testa criação de PUF óptico"""
        puf = OpticalPUF(material_seed=42)
        assert puf.get_id() is not None
    
    def test_speckle_pattern(self):
        """Testa geração de padrão de speckle"""
        puf = OpticalPUF(material_seed=42, speckle_size=64)
        pattern = puf.get_speckle_pattern()
        
        assert pattern.shape == (64, 64)
        assert pattern.min() >= 0
        assert pattern.max() <= 255
    
    def test_high_entropy(self):
        """Testa alta entropia de PUF óptico"""
        puf = OpticalPUF(material_seed=42, entropy_bits=512.0)
        assert puf.get_entropy() >= 256.0


class TestSRAMPUF:
    """Testes para SRAMPUF"""
    
    def test_creation(self):
        """Testa criação de SRAM PUF"""
        puf = SRAMPUF(chip_seed=42)
        assert puf.get_id() is not None
    
    def test_cell_stability(self):
        """Testa estabilidade de células"""
        puf = SRAMPUF(chip_seed=42, sram_size=1024)
        stability = puf.get_cell_stability()
        
        assert len(stability) == 1024 * 8  # bits
        assert stability.min() >= 0.0
        assert stability.max() <= 0.5
    
    def test_unstable_cells(self):
        """Testa contagem de células instáveis"""
        puf = SRAMPUF(chip_seed=42)
        unstable = puf.get_unstable_cells(threshold=0.1)
        
        # Deve haver algumas células instáveis (fonte de entropia)
        assert unstable > 0


def test_puf_protocol_compliance():
    """Testa conformidade com PUFProtocol"""
    pufs = [
        SimulatedPUF(seed=42),
        OpticalPUF(material_seed=42),
        SRAMPUF(chip_seed=42)
    ]
    
    for puf in pufs:
        # Todos devem ter estes métodos
        assert hasattr(puf, 'generate')
        assert hasattr(puf, 'get_entropy')
        assert hasattr(puf, 'get_ber')
        assert hasattr(puf, 'get_id')
        
        # Todos devem gerar resposta válida
        response = puf.generate()
        assert response.response is not None
        assert response.entropy_bits > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
