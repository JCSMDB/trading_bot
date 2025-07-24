"""
Scheduler pour tâches planifiées du bot de trading (quotidien, surveillance, etc.).
"""
import schedule
import threading
import asyncio
import time
from datetime import datetime
from typing import Callable
import logging

class TradingScheduler:
    """
    Scheduler pour exécuter des tâches à heure fixe et périodiquement, avec support async et threading.
    """
    def __init__(self, daily_time: str = "07:00"):
        self.daily_time = daily_time
        self._stop_event = threading.Event()
        self._thread = None

    def start(self, daily_task: Callable, monitor_task: Callable):
        """Démarre le scheduler avec les tâches fournies."""
        schedule.every().day.at(self.daily_time).do(self._wrap_async, daily_task)
        schedule.every(30).minutes.do(self._wrap_async, monitor_task)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop_event.is_set():
            if self._is_trading_day():
                schedule.run_pending()
            time.sleep(5)

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    @staticmethod
    def _is_trading_day() -> bool:
        # Pas de trading le samedi/dimanche
        return datetime.utcnow().weekday() < 5

    @staticmethod
    def _wrap_async(task: Callable):
        try:
            if asyncio.iscoroutinefunction(task):
                asyncio.run(task())
            else:
                task()
        except Exception as e:
            logging.error(f"Erreur dans la tâche planifiée: {e}") 