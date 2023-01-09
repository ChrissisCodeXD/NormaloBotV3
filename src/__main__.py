import os
from lightbulb.ext import tasks
from main import NormaloBot

if os.name != "nt":
    import uvloop

    uvloop.install()

if __name__ == "__main__":
    bot = NormaloBot()
    tasks.load(bot)
    bot.run()
