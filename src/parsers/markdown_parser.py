"""
Module de parsing des fichiers d'analyse markdown pour extraction des signaux de trading.
"""
import re
from typing import Optional
from src.models.trade_signal import TradeSignal

class MarkdownParseError(Exception):
    """Exception levée en cas d'erreur de parsing ou de validation du fichier markdown."""
    pass

class MarkdownAnalysisParser:
    """
    Parseur de fichiers markdown d'analyse pour extraire un signal de trading structuré.
    Gère les variantes de format, la validation stricte, et retourne un objet TradeSignal.
    """
    @staticmethod
    def parse_file(filepath: str) -> TradeSignal:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise MarkdownParseError(f"Erreur de lecture du fichier: {e}")
        return MarkdownAnalysisParser.parse_content(content)

    @staticmethod
    def parse_content(content: str) -> TradeSignal:
        # Extraction des sections
        actif = MarkdownAnalysisParser._extract_field(content, r'Actif\s*[:：]\s*([A-Z/]+)', True)
        direction = MarkdownAnalysisParser._extract_field(content, r'Direction\s*[:：]\s*(ACHAT|VENTE|BUY|SELL)', True)
        entry_price = MarkdownAnalysisParser._extract_field(content, r'(Entr[ée]e?|Entr\.|Entry)\s*[:：]\s*([\d.]+)', True, group=2)
        stop_loss = MarkdownAnalysisParser._extract_field(content, r'SL\s*[:：]\s*([\d.]+)', True)
        take_profit = MarkdownAnalysisParser._extract_field(content, r'TP\s*[:：]\s*([\d.]+)', True)
        risk = MarkdownAnalysisParser._extract_field(content, r'Risque\s*[:：]\s*([\d.,]+)%?', True)

        # Normalisation
        actif = actif.replace(' ', '').upper()
        direction = MarkdownAnalysisParser._normalize_direction(direction)
        try:
            entry_price = float(entry_price)
            stop_loss = float(stop_loss)
            take_profit = float(take_profit)
            risk_percentage = float(risk.replace(',', '.'))
        except Exception:
            raise MarkdownParseError("Erreur de conversion numérique sur un des paramètres (entrée, SL, TP, risque)")

        # Validation stricte
        if not actif or '/' not in actif:
            raise MarkdownParseError("Actif non reconnu ou manquant (ex: XAU/USD)")
        if direction not in ('BUY', 'SELL'):
            raise MarkdownParseError("Direction non reconnue (doit être BUY/SELL ou ACHAT/VENTE)")
        if not (0 < risk_percentage <= 100):
            raise MarkdownParseError("Le risque doit être entre 0 et 100%")
        if not (stop_loss < entry_price < take_profit) and direction == 'BUY':
            raise MarkdownParseError("Pour un BUY, SL < entrée < TP")
        if not (take_profit < entry_price < stop_loss) and direction == 'SELL':
            raise MarkdownParseError("Pour un SELL, TP < entrée < SL")

        return TradeSignal(
            symbol=actif,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_percentage=risk_percentage
        )

    @staticmethod
    def _extract_field(content: str, pattern: str, required: bool = False, group: int = 1) -> Optional[str]:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(group).strip()
        if required:
            raise MarkdownParseError(f"Champ obligatoire non trouvé: {pattern}")
        return None

    @staticmethod
    def _normalize_direction(direction: str) -> str:
        direction = direction.strip().upper()
        if direction in ('ACHAT', 'BUY'):
            return 'BUY'
        if direction in ('VENTE', 'SELL'):
            return 'SELL'
        raise MarkdownParseError(f"Direction inconnue: {direction}") 