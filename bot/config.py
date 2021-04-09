import sqlite3


TOKEN = 'TOKEN'

db = sqlite3.connect('hh_bot.db', check_same_thread=False)
cursor = db.cursor()

