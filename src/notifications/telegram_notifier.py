"""
Module de notifications Telegram pour le bot de trading.
"""
import requests
import time
import logging
from typing import Optional
from config.settings import get_settings

class TelegramNotifier:
    """
    Envoie des notifications Telegram formatées (HTML/Markdown), gère erreurs et rate limiting.
    """
    def __init__(self):
        self.settings = get_settings()
        self.api_url = f"https://api.telegram.org/bot{self.settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        self.chat_id = self.settings.TELEGRAM_CHAT_ID
        self.last_sent = 0
        self.min_interval = 1.2  # anti-flood

    def send(self, text: str, parse_mode: str = "HTML") -> bool:
        now = time.time()
        if now - self.last_sent < self.min_interval:
            time.sleep(self.min_interval - (now - self.last_sent))
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        try:
            resp = requests.post(self.api_url, data=payload, timeout=10)
            self.last_sent = time.time()
            if resp.status_code != 200:
                logging.error(f"Telegram: Erreur {resp.status_code} - {resp.text}")
                return False
            return True
        except Exception as e:
            logging.error(f"Telegram: Exception lors de l'envoi: {e}")
            return False

    def send_trade(self, symbol: str, direction: str, entry: float, sl: float, tp: float, risk: float):
        msg = (
            f"<b>Signal Trading</b>\n"
            f"Actif: <b>{symbol}</b>\n"
            f"Direction: <b>{direction}</b>\n"
            f"Entrée: <b>{entry}</b>\nSL: <b>{sl}</b>\nTP: <b>{tp}</b>\n"
            f"Risque: <b>{risk}%</b>"
        )
        return self.send(msg, parse_mode="HTML")

    def send_alert(self, text: str):
        msg = f"<b>ALERTE</b>\n{text}"
        return self.send(msg, parse_mode="HTML")

    def send_summary(self, text: str):
        msg = f"<b>Résumé du jour</b>\n{text}"
        return self.send(msg, parse_mode="HTML") 