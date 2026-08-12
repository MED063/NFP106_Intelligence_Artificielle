import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ChatBot


def run_cli(bot: ChatBot) -> None:
    print("=== ChatBot IA - Santé ===")
    print("Tapez 'quit' pour quitter.\n")
    feedback_count = 0
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    fb_path = os.path.join(data_dir, 'feedback_log.json')
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
            if feedback_count % 3 == 0:
                bot.retrain()
                print("[Modèle mis à jour après 3 retours]")


if __name__ == '__main__':
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    bot = ChatBot(data_dir=data_dir + os.sep)
    run_cli(bot)
