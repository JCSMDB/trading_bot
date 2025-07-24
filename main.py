"""
Point d'entrée du bot de trading automatisé.
"""
import logging
import os
from config.settings import get_settings
from src.parsers.markdown_parser import MarkdownAnalysisParser, MarkdownParseError
from src.brokers.mt5_broker import MT5Broker
from src.database.trade_logger import TradeLogger
from src.notifications.telegram_notifier import TelegramNotifier
from src.utils.scheduler import TradingScheduler
from datetime import datetime
import traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class TradingBot:
    """
    Bot principal : routine quotidienne, gestion des signaux, exécution, logging, sécurité.
    """
    def __init__(self):
        self.settings = get_settings()
        self.broker = MT5Broker()
        self.logger = TradeLogger(self.settings.DATABASE_PATH)
        self.notifier = TelegramNotifier()
        self.scheduler = TradingScheduler(self.settings.EXECUTION_TIME)
        self.running = False

    def start(self):
        self.running = True
        self.scheduler.start(self.daily_routine, self.monitor_positions)
        logging.info("Bot démarré. Appuyez sur Ctrl+C pour arrêter.")
        try:
            while self.running:
                pass  # Le scheduler tourne en thread
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        self.scheduler.stop()
        logging.info("Bot arrêté.")

    def daily_routine(self):
        """Routine quotidienne : parse analyse, valider, exécuter, log, notifier."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            analysis_file = os.path.join(self.settings.ANALYSIS_FOLDER, f"{today}.md")
            if not os.path.exists(analysis_file):
                msg = f"Aucune analyse trouvée pour aujourd'hui ({today}) : {analysis_file}"
                logging.warning(msg)
                self.notifier.send_alert(msg)
                return
            signal = MarkdownAnalysisParser.parse_file(analysis_file)
            # Validation stricte du signal
            if not self._validate_signal(signal):
                self.notifier.send_alert("Signal du jour invalide, trading annulé.")
                return
            # Exécution du trade
            execution_info = self.broker.execute_trade(signal)
            signal_id = self.logger.save_signal(signal.dict())
            execution_id = self.logger.save_execution({
                'signal_id': signal_id,
                'execution_time': datetime.now().isoformat(),
                'order_id': execution_info.get('order'),
                'position_id': execution_info.get('position'),
                'executed_price': execution_info.get('price'),
                'volume': execution_info.get('volume')
            })
            self.notifier.send_trade(signal.symbol, signal.direction, signal.entry_price, signal.stop_loss, signal.take_profit, signal.risk_percentage)
            logging.info(f"Trade exécuté et loggé (signal_id={signal_id}, execution_id={execution_id})")
        except MarkdownParseError as e:
            logging.error(f"Erreur parsing analyse: {e}")
            self.notifier.send_alert(f"Erreur parsing analyse: {e}")
        except Exception as e:
            logging.error(f"Erreur critique dans la routine quotidienne: {e}\n{traceback.format_exc()}")
            self.notifier.send_alert(f"Erreur critique: {e}")
            self.stop()

    def monitor_positions(self):
        """Surveillance périodique des positions pour break-even, fermeture, etc."""
        try:
            positions = self.broker.get_open_positions()
            for pos in positions or []:
                # Exemple : break-even automatique si gain > 1R
                if pos.profit > 0 and not self._is_break_even(pos):
                    new_sl = pos.price_open
                    self.broker.modify_position(pos.ticket, stop_loss=new_sl)
                    self.notifier.send_alert(f"SL déplacé au break-even pour la position {pos.ticket}")
        except Exception as e:
            logging.error(f"Erreur surveillance positions: {e}")

    def _validate_signal(self, signal) -> bool:
        # Validation stricte du risk, symbol, direction, etc.
        if signal.risk_percentage > self.settings.RISK_PERCENTAGE:
            logging.error("Le risque du signal dépasse le maximum autorisé.")
            return False
        # Vérification du capital disponible (exemple simplifié)
        if self.settings.CAPITAL_INITIAL <= 0:
            logging.error("Capital initial non valide.")
            return False
        # Vérification du symbole
        mapped = self.broker.map_symbol(signal.symbol)
        if not mapped.isalnum():
            logging.error("Symbole non valide pour le broker.")
            return False
        return True

if __name__ == "__main__":
    bot = TradingBot()
    bot.start() 