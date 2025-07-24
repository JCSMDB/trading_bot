"""
Implémentation du broker MetaTrader5 pour le bot de trading automatisé.
"""
import MetaTrader5 as mt5
from src.brokers.base_broker import BaseBroker
from src.models.trade_signal import TradeSignal
from config.settings import get_settings
from typing import Any, Dict, Optional
import time
import logging
import threading

class MT5Broker(BaseBroker):
    """
    Broker MetaTrader5 : connexion, exécution d'ordres, gestion des positions, mapping symboles, calcul taille.
    """
    def __init__(self):
        self.settings = get_settings()
        self.connected = False
        self._lock = threading.Lock()

    def connect(self) -> bool:
        with self._lock:
            if self.connected:
                return True
            if not mt5.initialize(
                login=int(self.settings.MT5_LOGIN),
                password=self.settings.MT5_PASSWORD,
                server=self.settings.MT5_SERVER
            ):
                logging.error(f"MT5: Échec de connexion: {mt5.last_error()}")
                self.connected = False
                return False
            self.connected = True
            return True

    def is_connected(self) -> bool:
        return self.connected and mt5.terminal_info() is not None

    def execute_trade(self, signal: TradeSignal) -> Dict[str, Any]:
        if not self.is_connected():
            if not self.connect():
                raise RuntimeError("Impossible de se connecter à MT5")
        symbol = self.map_symbol(signal.symbol)
        lot = self.calculate_position_size(signal, self.settings.CAPITAL_INITIAL)
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Symbole {symbol} non disponible sur MT5")
        order_type = mt5.ORDER_TYPE_BUY if signal.direction == 'BUY' else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).ask if signal.direction == 'BUY' else mt5.symbol_info_tick(symbol).bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": signal.stop_loss,
            "tp": signal.take_profit,
            "deviation": 20,
            "magic": 123456,
            "comment": "BotAuto",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"MT5: Erreur d'exécution: {result.retcode} - {result.comment}")
            raise RuntimeError(f"Erreur d'exécution MT5: {result.retcode} - {result.comment}")
        return {
            "order": result.order,
            "position": result.position,
            "price": result.price,
            "volume": result.volume,
            "symbol": symbol,
            "direction": signal.direction
        }

    def modify_position(self, position_id: Any, stop_loss: Optional[float]=None, take_profit: Optional[float]=None) -> bool:
        if not self.is_connected():
            self.connect()
        pos = mt5.positions_get(ticket=position_id)
        if not pos:
            logging.error(f"MT5: Position {position_id} introuvable")
            return False
        position = pos[0]
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": position_id,
            "sl": stop_loss if stop_loss else position.sl,
            "tp": take_profit if take_profit else position.tp,
            "symbol": position.symbol,
            "magic": 123456,
            "comment": "BotAuto-Modif"
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"MT5: Erreur modification SL/TP: {result.retcode}")
            return False
        return True

    def close_position(self, position_id: Any) -> bool:
        if not self.is_connected():
            self.connect()
        pos = mt5.positions_get(ticket=position_id)
        if not pos:
            logging.error(f"MT5: Position {position_id} introuvable pour fermeture")
            return False
        position = pos[0]
        order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(position.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": position_id,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "BotAuto-Close"
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"MT5: Erreur fermeture position: {result.retcode}")
            return False
        return True

    def get_open_positions(self) -> list:
        if not self.is_connected():
            self.connect()
        return mt5.positions_get()

    def calculate_position_size(self, signal: TradeSignal, capital: float) -> float:
        # Calcul du lot basé sur le risque % et la distance SL
        risk_amount = capital * (signal.risk_percentage / 100)
        sl_distance = abs(signal.entry_price - signal.stop_loss)
        if sl_distance == 0:
            raise ValueError("Distance SL nulle")
        # Hypothèse: 1 lot = 100 000 unités, pip = 0.01 pour XAU/USD, 0.0001 pour FX
        pip_value = 0.01 if 'XAU' in signal.symbol else 0.0001
        lot_size = risk_amount / (sl_distance / pip_value * 10)
        lot_size = max(0.01, round(lot_size, 2))
        return lot_size

    def map_symbol(self, symbol: str) -> str:
        # Mapping simple : EUR/USD -> EURUSD, XAU/USD -> XAUUSD
        return symbol.replace('/', '').upper() 