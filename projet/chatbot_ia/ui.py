"""
ce fichier implemente l'interface utilisateur du ChatBot IA, qui peut etre lancee en mode CLI (ligne de commande) ou via un serveur web Flask.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from main import ChatBot


def run_cli(bot: ChatBot) -> None:
    print("=== ChatBot IA - Santé ===")
    print("Tapez 'quit' pour quitter.\n")
    feedback_count = 0
    fb_path = config.FEEDBACK_LOG
    while True:
        user_input = input("\nVous : ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "quitter", "exit", "q"):
            print("Bot : Au revoir !")
            bot.learner.save_feedback(fb_path)
            break
        response = bot.answer(user_input)
        print(f"Bot : {response}")

        fb = input("Note (1-5, Entrée pour passer) : ").strip()
        if fb.isdigit() and 1 <= int(fb) <= 5:
            bot.learner.record_feedback(user_input, response, int(fb))
            feedback_count += 1
            if feedback_count % config.FEEDBACK_RETRAIN_EVERY == 0:
                bot.retrain()
                print(f"[Modèle mis à jour après {config.FEEDBACK_RETRAIN_EVERY} retours]")


if __name__ == '__main__':
    bot = ChatBot(data_dir=config.DATA_DIR)
    run_cli(bot)
