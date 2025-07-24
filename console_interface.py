"""
Interface console interactive pour le bot de trading automatisé.
"""
import pandas as pd
from src.database.trade_logger import TradeLogger
from src.brokers.mt5_broker import MT5Broker
from config.settings import get_settings
import sys

class ConsoleInterface:
    """
    Menu interactif : historique, stats, positions, export, nettoyage.
    """
    def __init__(self):
        self.settings = get_settings()
        self.logger = TradeLogger(self.settings.DATABASE_PATH)
        self.broker = MT5Broker()

    def run(self):
        while True:
            print("\n--- MENU BOT TRADING ---")
            print("1. Historique des signaux")
            print("2. Statistiques de performance")
            print("3. Positions ouvertes")
            print("4. Exporter une table en CSV")
            print("5. Nettoyer la base de données")
            print("0. Quitter")
            choice = input("Choix : ")
            try:
                if choice == '1':
                    self.show_signals_history()
                elif choice == '2':
                    self.show_performance_stats()
                elif choice == '3':
                    self.show_open_positions()
                elif choice == '4':
                    self.export_csv()
                elif choice == '5':
                    self.clean_db()
                elif choice == '0':
                    print("Au revoir !")
                    sys.exit(0)
                else:
                    print("Choix invalide.")
            except Exception as e:
                print(f"Erreur : {e}")

    def show_signals_history(self):
        df = self.logger.get_signals_history()
        print(df.to_string(index=False))

    def show_performance_stats(self):
        df = self.logger.get_performance_stats()
        print(df.to_string(index=False))

    def show_open_positions(self):
        positions = self.broker.get_open_positions()
        if not positions:
            print("Aucune position ouverte.")
            return
        data = [{
            'Ticket': p.ticket,
            'Symbole': p.symbol,
            'Direction': 'BUY' if p.type == 0 else 'SELL',
            'Volume': p.volume,
            'Prix entrée': p.price_open,
            'SL': p.sl,
            'TP': p.tp,
            'Profit': p.profit
        } for p in positions]
        df = pd.DataFrame(data)
        print(df.to_string(index=False))

    def export_csv(self):
        table = input("Nom de la table à exporter (trade_signals, trade_executions, trade_results, daily_performance) : ")
        path = input("Chemin du fichier CSV à créer : ")
        self.logger.export_csv(table, path)
        print(f"Table {table} exportée vers {path}")

    def clean_db(self):
        days = int(input("Supprimer les données de plus de combien de jours ? "))
        deleted = self.logger.clean_old_data(days)
        print(f"{deleted} lignes supprimées.")

if __name__ == "__main__":
    ConsoleInterface().run() 