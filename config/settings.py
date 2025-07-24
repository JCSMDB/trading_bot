"""
Module de configuration centralisé utilisant Pydantic pour la validation et la gestion des paramètres d'environnement.
"""
from pydantic import BaseSettings, Field, validator
from typing import Literal
import os

class Settings(BaseSettings):
    CAPITAL_INITIAL: float = Field(10000.0, gt=0, description="Capital initial du compte")
    RISK_PERCENTAGE: float = Field(1.0, gt=0, le=100, description="Pourcentage de risque par trade")
    ACTIVE_BROKER: Literal['MT5'] = Field('MT5', description="Broker actif (MT5 uniquement pour l'instant)")
    MT5_LOGIN: str = Field(..., description="Identifiant de connexion MT5")
    MT5_PASSWORD: str = Field(..., description="Mot de passe MT5")
    MT5_SERVER: str = Field(..., description="Serveur MT5")
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Token du bot Telegram")
    TELEGRAM_CHAT_ID: str = Field(..., description="ID du chat Telegram")
    EXECUTION_TIME: str = Field('07:00', regex=r'^\d{2}:\d{2}$', description="Heure d'exécution quotidienne (HH:MM)")
    DATABASE_PATH: str = Field('./data/trades.db', description="Chemin vers la base de données SQLite")
    ANALYSIS_FOLDER: str = Field('./data/analyses', description="Dossier des analyses markdown")

    @validator('DATABASE_PATH', 'ANALYSIS_FOLDER')
    def check_path_exists(cls, v):
        # On ne crée pas ici, mais on vérifie le format
        if not isinstance(v, str) or not v:
            raise ValueError('Le chemin doit être une chaîne non vide')
        return v

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '../.env')
        env_file_encoding = 'utf-8'

def get_settings() -> Settings:
    """Retourne une instance unique de Settings (singleton)."""
    if not hasattr(get_settings, "_settings"):
        get_settings._settings = Settings()
    return get_settings._settings 