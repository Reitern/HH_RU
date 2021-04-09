import func_bot
import functions
import telebot
from telebot import types
from config import (db, cursor, TOKEN)


is_running = False
city = ''
country = ''

bot = telebot.TeleBot(TOKEN)

country_keyboard = types.InlineKeyboardMarkup()
country_keyboard.add(types.InlineKeyboardButton(text='Россия', callback_data='rus'))
country_keyboard.add(types.InlineKeyboardButton(text='Украина', callback_data='ukr'))

result_keyboard = types.InlineKeyboardMarkup()
result_keyboard.add(types.InlineKeyboardButton(text='Максимальная зарплата', callback_data='max'))
result_keyboard.add(types.InlineKeyboardButton(text='Минимальная зарплата', callback_data='min'))
result_keyboard.add(types.InlineKeyboardButton(text='Средняя зарплата', callback_data='avg'))

# создание таблицы
func_bot.create_tables()
db.commit()


@bot.message_handler(commands=['start'])
def start_command(message):
    global is_running
    if not is_running:
        bot.send_message(message.from_user.id, "Привет, {}".format(message.from_user.first_name))
        question = "Из какой ты страны?"
        bot.send_message(message.from_user.id, text=question, reply_markup=country_keyboard)
        is_running = True


def ask_city(message):
    global city, is_running
    chat_id = message.chat.id
    text = message.text
    if not all(x.isalpha() or x.isspace() for x in text):
        msg = bot.send_message(chat_id, 'Название города должно состоять из букв, попробуй ещё раз')
        bot.register_next_step_handler(msg, ask_city)
        return
    city = ''
    for word in text.split():
        city = city + word.capitalize() + ' '
    city = city.strip()
    if functions.fnd_city_id(country, city) == 0:
        msg = bot.send_message(chat_id, 'Ой, я не знаю такой город. Попробуй ещё раз')
        bot.register_next_step_handler(msg, ask_city)
        return
    else:
        bot.send_message(chat_id, 'Спасибо, я запомнил что ты из города ' + city)
        is_running = False


@bot.message_handler(commands=['changecity'])
def change_city(message):
    global is_running
    if not is_running:
        question = "Из какой ты страны?"
        bot.send_message(message.from_user.id, text=question, reply_markup=country_keyboard)
        is_running = True


@bot.message_handler(commands=['getresult'])
def change_city(message):
    if city == '' or functions.fnd_city_id(country, city) == 0:
        bot.send_message(message.chat.id, 'Пожалуйста, введи название города правильно через /changecity')
    else:
        if not func_bot.get_from_main(city):
            bot.send_message(message.chat.id, 'Пожалуйста подожди...')
            func_bot.load_data(country, city)
        question = "Что тебя интересует?"
        bot.send_message(message.from_user.id, text=question, reply_markup=result_keyboard)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == "город":
        bot.send_message(message.from_user.id, country)
        bot.send_message(message.from_user.id, city)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global country, city
    city_name = [(str(city))]
    if call.data == "rus":
        country = 'Россия'
        msg = bot.send_message(call.message.chat.id, "Из какого ты города?")
        bot.register_next_step_handler(msg, ask_city)
    elif call.data == "ukr":
        country = 'Украина'
        msg = bot.send_message(call.message.chat.id, "Из какого ты города?")
        bot.register_next_step_handler(msg, ask_city)
    elif call.data == "max":
        cursor.execute(f"SELECT salary_to FROM main_cities WHERE city_name = ?", city_name)
        result = cursor.fetchone()
        bot.send_message(call.message.chat.id, "Максимальная ЗП: " + str(result[0]))
    elif call.data == "min":
        cursor.execute(f"SELECT salary_from FROM main_cities WHERE city_name = ?", city_name)
        result = cursor.fetchone()
        bot.send_message(call.message.chat.id, "Максимальная ЗП: " + str(result[0]))
    elif call.data == "avg":
        cursor.execute(f"SELECT avg_salary FROM main_cities WHERE city_name = ?", city_name)
        result = cursor.fetchone()
        bot.send_message(call.message.chat.id, "Cредняя ЗП: " + str(round(result[0])))


bot.polling(none_stop=True, interval=0)
