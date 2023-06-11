from src import TravBot, create_rotating_log
import os

logfile = 'Log.txt'
mainlogger = create_rotating_log(logfile)

bot = TravBot(debug=True)
bot.run()
