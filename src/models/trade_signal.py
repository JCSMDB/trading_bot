"""
Modèle de données pour un signal de trading extrait d'un fichier d'analyse.
"""
from pydantic import BaseModel, Field, validator
from typing import Literal

class TradeSignal(BaseModel):
    symbol: str = Field(..., description="Symbole de l'actif, ex: XAU/USD")
    direction: Literal['BUY', 'SELL'] = Field(..., description="Direction du trade (BUY ou SELL)")
    entry_price: float = Field(..., gt=0, description="Prix d'entrée")
    stop_loss: float = Field(..., gt=0, description="Stop loss")
    take_profit: float = Field(..., gt=0, description="Take profit")
    risk_percentage: float = Field(..., gt=0, le=100, description="Pourcentage de risque sur le capital")

    @validator('symbol')
    def validate_symbol(cls, v):
        if '/' not in v:
            raise ValueError('Le symbole doit être au format XXX/YYY')
        return v.upper()

    @validator('direction')
    def validate_direction(cls, v):
        if v not in ('BUY', 'SELL'):
            raise ValueError('La direction doit être BUY ou SELL')
        return v 