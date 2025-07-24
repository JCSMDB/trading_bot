# Trading Bot Automatisé

Ce projet est un bot de trading automatisé en Python, conçu pour exécuter des signaux de trading à partir de fichiers d'analyse markdown, avec gestion du risque, exécution sur MetaTrader5, notifications Telegram, et base de données SQLite.

## Installation

1. Clonez le dépôt et placez-vous dans le dossier `trading_bot`.
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Copiez `.env.example` vers `.env` et renseignez vos informations de connexion et paramètres.

## Structure du projet

Voir l'arborescence dans le prompt d'origine.

## Utilisation

- Lancement du bot :
  ```bash
  python main.py
  ```
- Interface console :
  ```bash
  python console_interface.py
  ```
- Test des modules :
  ```bash
  python -c "from src.parsers.markdown_parser import MarkdownAnalysisParser; print('✅ Parser OK')"
  python -c "from config.settings import get_settings; print('✅ Config OK')"
  ```

## Fichier d'analyse markdown (exemple)

```markdown
# Analyse du 2025-07-24

## Stratégie
Actif: XAU/USD
Direction: ACHAT
Entrée: 2345.00

## Paramètres
SL: 2335.00
TP: 2375.00
Risque: 1.5%

## Récapitulatif
Confiance: ÉLEVÉE
Timeframe: H4
```

## Sécurité & Bonnes pratiques
- Validation stricte des signaux et du risque
- Jamais d'exécution sans analyse valide du jour
- Arrêt automatique en cas d'erreur critique
- Logs détaillés pour audit

## Dépendances principales
- MetaTrader5, pandas, pydantic, python-dotenv, requests, schedule

## Licence
MIT 