import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ChatBot


def run_cli(bot: ChatBot) -> None:
    print("=== ChatBot IA - Informatique ===")
    print("Tapez 'quit' pour quitter.\n")
    while True:
        user_input = input("Vous : ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "quitter", "exit", "q"):
            print("Bot : Au revoir !")
            break
        response = bot.answer(user_input)
        print(f"Bot : {response}")

        fb = input("Note (1-5, Entrée pour passer) : ").strip()
        if fb.isdigit() and 1 <= int(fb) <= 5:
            bot.learner.record_feedback(user_input, response, int(fb))


if __name__ == '__main__':
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    bot = ChatBot(data_dir=data_dir + os.sep)
    run_cli(bot)
