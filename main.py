from lib.context import Context
from lib.telegram import AyaLangBot

def main():
    context = Context()
    bot = AyaLangBot(context)
    print("Starting bot...")
    bot.run()

if __name__ == "__main__":
    main()
