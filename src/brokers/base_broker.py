"""
Interface abstraite pour les brokers de trading.
"""
from abc import ABC, abstractmethod
from src.models.trade_signal import TradeSignal
from typing import Any, Dict, Optional

class BaseBroker(ABC):
    """
    Interface de base pour l'intégration d'un broker de trading.
    """
    @abstractmethod
    def connect(self) -> bool:
        """Se connecte au broker. Retourne True si succès."""
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """Vérifie l'état de connexion."""
        raise NotImplementedError

    @abstractmethod
    def execute_trade(self, signal: TradeSignal) -> Dict[str, Any]:
        """Exécute un trade (market ou limit) selon le signal. Retourne les infos d'exécution."""
        raise NotImplementedError

    @abstractmethod
    def modify_position(self, position_id: Any, stop_loss: Optional[float]=None, take_profit: Optional[float]=None) -> bool:
        """Modifie SL/TP d'une position ouverte."""
        raise NotImplementedError

    @abstractmethod
    def close_position(self, position_id: Any) -> bool:
        """Ferme une position ouverte."""
        raise NotImplementedError

    @abstractmethod
    def get_open_positions(self) -> list:
        """Retourne la liste des positions ouvertes."""
        raise NotImplementedError

    @abstractmethod
    def calculate_position_size(self, signal: TradeSignal, capital: float) -> float:
        """Calcule la taille de position en fonction du risque et du capital."""
        raise NotImplementedError

    @abstractmethod
    def map_symbol(self, symbol: str) -> str:
        """Mappe le symbole standard (ex: EUR/USD) vers le format broker (ex: EURUSD)."""
        raise NotImplementedError 