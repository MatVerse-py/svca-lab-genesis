import numpy as np
import hashlib
import json
from typing import List, Dict, Any

class AdaptiveOmega:
    """
    Motor de Ω Adaptativo.
    Substitui regras fixas por pesos aprendidos que definem a 'energia de admissibilidade'.
    O sistema descobre as regras de sobrevivência do estado Ψ.
    """
    def __init__(self, input_dim: int = 8, learning_rate: float = 0.01):
        self.input_dim = input_dim
        self.lr = learning_rate
        # Pesos das regras Σ (inicializados aleatoriamente)
        self.weights = np.random.randn(input_dim)
        self.bias = np.random.randn()
        self.history = []

    def calculate_admissibility(self, state_vector: np.ndarray) -> float:
        """Calcula a energia de admissibilidade (Ω-Energy)"""
        # E = Σ (w_i * state_i) + b
        energy = np.dot(self.weights, state_vector) + self.bias
        # Ativação Sigmoide para probabilidade de admissão
        return 1.0 / (1.0 + np.exp(-energy))

    def adapt(self, state_vector: np.ndarray, outcome: float):
        """
        Ajusta os pesos com base no desfecho (outcome).
        Outcome > 0: Estado estável (reforça regra)
        Outcome < 0: Estado instável/ataque (ajusta para evitar)
        """
        prediction = self.calculate_admissibility(state_vector)
        error = outcome - prediction
        
        # Gradiente descendente simples
        self.weights += self.lr * error * state_vector
        self.bias += self.lr * error
        
        self.history.append({
            "weights": self.weights.copy().tolist(),
            "error": float(error)
        })

    def get_rules_summary(self) -> Dict[str, float]:
        """Traduz pesos aprendidos em importância de regras"""
        rule_names = ["Time", "Entropy", "PUF_Stability", "BER", "Temp", "Voltage", "Jitter", "Network"]
        summary = {}
        normalized_weights = np.abs(self.weights) / np.sum(np.abs(self.weights))
        for name, weight in zip(rule_names, normalized_weights):
            summary[name] = float(weight)
        return summary

    def save_model(self, path: str):
        model_data = {
            "weights": self.weights.tolist(),
            "bias": self.bias,
            "input_dim": self.input_dim,
            "summary": self.get_rules_summary()
        }
        with open(path, "w") as f:
            json.dump(model_data, f, indent=2)

    @classmethod
    def load_model(cls, path: str):
        with open(path, "r") as f:
            data = json.load(f)
        instance = cls(input_dim=data["input_dim"])
        instance.weights = np.array(data["weights"])
        instance.bias = data["bias"]
        return instance
