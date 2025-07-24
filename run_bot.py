"""
Script de lancement unique pour le bot de trading automatisé (Windows, PyInstaller).
Permet de lancer le bot principal ou l'interface console via un menu.
"""
import os
import sys

# S'assurer que le dossier courant est le bon
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Vérifier la présence du .env
if not os.path.exists('.env'):
    print("Le fichier .env est manquant. Copiez .env.example vers .env et configurez vos paramètres avant de lancer le bot.")
    sys.exit(1)


def main_menu():
    print("\n=== BOT DE TRADING AUTOMATISÉ ===")
    print("1. Lancer le bot principal (exécution automatique)")
    print("2. Lancer l'interface console (historique, stats, export)")
    print("0. Quitter")
    return input("Votre choix : ")

if __name__ == "__main__":
    while True:
        choix = main_menu()
        if choix == '1':
            os.system(f'{sys.executable} main.py')
        elif choix == '2':
            os.system(f'{sys.executable} console_interface.py')
        elif choix == '0':
            print("Au revoir !")
            sys.exit(0)
        else:
            print("Choix invalide.") 