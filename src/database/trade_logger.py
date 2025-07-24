"""
Gestionnaire de base de données SQLite pour le bot de trading.
"""
import sqlite3
from typing import Any, Dict, List, Optional
import pandas as pd
import os
import logging
from datetime import datetime

class TradeLogger:
    """
    Gère la base SQLite : signaux, exécutions, résultats, stats, export, nettoyage.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_tables(self):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS trade_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                symbol TEXT,
                direction TEXT,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                risk_percentage REAL
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS trade_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                execution_time TEXT,
                order_id TEXT,
                position_id TEXT,
                executed_price REAL,
                volume REAL,
                FOREIGN KEY(signal_id) REFERENCES trade_signals(id)
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS trade_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER,
                close_time TEXT,
                close_price REAL,
                pnl REAL,
                result TEXT,
                FOREIGN KEY(execution_id) REFERENCES trade_executions(id)
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS daily_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_pnl REAL,
                trades_count INTEGER
            )''')
            conn.commit()

    def save_signal(self, signal: Dict[str, Any]) -> int:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO trade_signals (date, symbol, direction, entry_price, stop_loss, take_profit, risk_percentage)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (datetime.now().strftime('%Y-%m-%d'), signal['symbol'], signal['direction'], signal['entry_price'],
                       signal['stop_loss'], signal['take_profit'], signal['risk_percentage']))
            conn.commit()
            return c.lastrowid

    def save_execution(self, execution: Dict[str, Any]) -> int:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO trade_executions (signal_id, execution_time, order_id, position_id, executed_price, volume)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (execution['signal_id'], execution['execution_time'], execution['order_id'], execution['position_id'],
                       execution['executed_price'], execution['volume']))
            conn.commit()
            return c.lastrowid

    def save_trade_result(self, result: Dict[str, Any]) -> int:
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO trade_results (execution_id, close_time, close_price, pnl, result)
                         VALUES (?, ?, ?, ?, ?)''',
                      (result['execution_id'], result['close_time'], result['close_price'], result['pnl'], result['result']))
            conn.commit()
            return c.lastrowid

    def get_performance_stats(self, start_date: Optional[str]=None, end_date: Optional[str]=None) -> pd.DataFrame:
        query = 'SELECT * FROM daily_performance'
        params = []
        if start_date and end_date:
            query += ' WHERE date BETWEEN ? AND ?'
            params = [start_date, end_date]
        with self._connect() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df

    def get_signals_history(self, limit: int=100) -> pd.DataFrame:
        with self._connect() as conn:
            df = pd.read_sql_query('SELECT * FROM trade_signals ORDER BY id DESC LIMIT ?', conn, params=(limit,))
        return df

    def export_csv(self, table: str, export_path: str) -> None:
        with self._connect() as conn:
            df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
            df.to_csv(export_path, index=False)

    def clean_old_data(self, days: int=365) -> int:
        cutoff = (datetime.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM trade_signals WHERE date < ?', (cutoff,))
            c.execute('DELETE FROM trade_executions WHERE execution_time < ?', (cutoff,))
            c.execute('DELETE FROM trade_results WHERE close_time < ?', (cutoff,))
            c.execute('DELETE FROM daily_performance WHERE date < ?', (cutoff,))
            deleted = c.rowcount
            conn.commit()
        logging.info(f"Nettoyage BDD : {deleted} lignes supprimées")
        return deleted 