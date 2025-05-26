import random
from datetime import datetime, timedelta
from database import *
from telebot import types
import telebot
import google_api
import config

db = Database(config.database_path)
bot_token = config.test_bot_token
bot = telebot.TeleBot(bot_token)
CHAT_BY_DATETIME = dict()

def write_statistics(statistics_type, user_id):
    now = datetime.now().strftime("%d.%m.%y")
    date_list = db.get_date_str_statistics()
    if now not in date_list:
        db.write_new_date_statistics()
    db.write_statistics(statistics_type, user_id)


def get_date(now, days_cnt):
    return (now + timedelta(days=days_cnt)).strftime("%d.%m.%y")


@bot.message_handler(commands=['start'])
def start(message):
    db.create_db()
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!')
    if db.check_new_user(message.from_user.id):
        get_new_user_info_step1(message)
    else:
        wait_command(message)


def get_new_user_info_step1(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text="Отправить номер телефона",
                                request_contact=True)
    markup.row(btn1)
    bot.send_message(message.chat.id, f'Чтобы начать пользоваться ботом необходимо поделиться номером!\n', reply_markup=markup)
    bot.register_next_step_handler(message, get_new_user_info_step2)

def get_new_user_info_step2(message):
    if message.contact:
        number = message.contact.phone_number
        db.write_new_user(message, number)
        write_statistics("new_user", message.from_user.id)
        wait_command(message)
    else:
        bot.send_message(message.chat.id, f'Нажмите на кнопку "Отправить номер телефона"')
        get_new_user_info_step1(message)



@bot.message_handler(commands=['newsletter'])
def newsletter(message):
    if message.from_user.id == config.admin_tg_id:
        bot.send_message(message.chat.id, f'Введи текст рассылки!')
        bot.register_next_step_handler(message, newsletter_step2)


def newsletter_step2(message):
    text = message.text
    chat_id_list = db.get_chat_id_list()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Сделать рассылку')
    btn2 = types.KeyboardButton('Отмена')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, f'Количество получателей: {len(chat_id_list)}. Им будет направлена следующая рассылка:\n{text}', reply_markup=markup)
    bot.register_next_step_handler(message, newsletter_step3, chat_id_list, text)


def newsletter_step3(message, chat_id_list, text):
    if 'сделать рассылку' in message.text.lower():
        if len(chat_id_list) > 0:
            for chat_id in chat_id_list:
                try:
                    bot.send_message(chat_id, text)
                except Exception as e:
                    print("Произошла ошибка:", e)
        else:
            bot.send_message(message.chat.id, f'Отсутствуют получатели, рассылка невозможна')
    elif message.text.lower() != "отмена":
        bot.send_message(message.chat.id, f'Неизвестная команда')
    return wait_command(message)


def wait_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Забронировать столик')
    btn2 = types.KeyboardButton('Мое бронирование')
    markup.row(btn1)
    markup.row(btn2)
    bot.send_message(message.chat.id, f'Выбери команду\n', reply_markup=markup)
    return bot.register_next_step_handler(message, info)


@bot.message_handler()
def info(message):
    if check_dubl_message(message):
        return
    if message.text is None:
        pass
    if db.check_new_user(message.from_user.id):
        return get_new_user_info_step1(message)
    elif message.text.lower() == '/start':
        return start(message)
    elif message.text.lower() == '/newsletter':
        return newsletter(message)
    elif message.text.lower() == 'забронировать столик':
        my_hall, my_date, my_time, my_table, my_people_cnt = get_my_book(message.from_user.id)
        if my_table != '':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn1 = types.KeyboardButton('Да')
            btn2 = types.KeyboardButton('Нет')
            markup.row(btn1, btn2)
            bot.send_message(message.chat.id, f'У вас уже забронирован столик, хотите отметить предыдущую бронь?', reply_markup=markup)
            return bot.register_next_step_handler(message, delete_booking)
        return choose_hall(message)
    elif message.text.lower() == 'мое бронирование':
        print_my_booking(message)
    else:
        bot.send_message(message.chat.id, '<b>Я пока не знаю такой команды</b>', parse_mode='html')
    return wait_command(message)


def print_my_booking(message):
    my_hall, my_date, my_time, my_table, my_people_cnt = get_my_book(message.from_user.id)
    if my_table != '':
        bot.send_message(message.chat.id,
                         f'Ваша бронь: {my_hall} {my_date} в {my_time} {my_table}, гостей {my_people_cnt}, '
                         f'продолжительность бронирования {config.book_duration}ч.')
    else:
        bot.send_message(message.chat.id, f'Вы пока ничего не забронировали!')


def get_my_book(user_id):
    my_hall = db.get_user_parameter(user_id, "book_hall")
    my_date = db.get_user_parameter(user_id, "book_date")
    my_time = db.get_user_parameter(user_id, "book_time")
    my_table = db.get_user_parameter(user_id, "book_table")
    my_people_cnt = db.get_user_parameter(user_id, "book_people_cnt")
    return my_hall, my_date, my_time, my_table, my_people_cnt


def delete_booking(message):
    if message.text.lower() == 'да':
        my_hall, my_date, my_time, my_table, my_people_cnt = get_my_book(message.from_user.id)
        error = google_api.write_sheet(my_hall, my_date, my_time, '', my_table, is_deleting=1)
        db.write_user_parameter(message.from_user.id, 'book_hall', '')
        db.write_user_parameter(message.from_user.id, 'book_date', '')
        db.write_user_parameter(message.from_user.id, 'book_time', '')
        db.write_user_parameter(message.from_user.id, 'book_table', '')
        bot.send_message(message.chat.id, f'Бронирование успешно удалено!')
        return choose_hall(message)
    else:
        return wait_command(message)



def choose_hall(message):
    img = open(config.hall_img, 'rb')
    bot.send_message(message.chat.id, f'В нашем караоке-баре два зала: караоке-зал и лаундж-зал. Вот его схема.')
    bot.send_photo(message.chat.id, img)
    markup = types.InlineKeyboardMarkup(row_width=config.row_width)
    btn1 = types.InlineKeyboardButton(text="Караоке-зал", callback_data="Караоке-зал")
    btn2 = types.InlineKeyboardButton(text="Лаундж-зал", callback_data="Лаундж-зал")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f'Выбери зал', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data)
def book_processing(callback):
    new_info_list, new_text = get_callback_list_and_text(callback.data, callback.message.chat.id)
    if new_text == '':
        bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.id)
        my_hall, my_date, my_time, my_table, my_people_cnt = get_my_book(callback.message.chat.id)
        first_name = db.get_user_parameter(callback.message.chat.id, "first_name")
        error = google_api.write_sheet(my_hall, my_date, my_time, first_name, my_table)
        if error == 0:
            bot.send_message(callback.message.chat.id, f'Успешно забронировано!\nВаша бронь: {my_hall}'
                                                       f'{my_date} в {my_time} {my_table}, гостей {my_people_cnt}, '
                                                       f'продолжительность бронирования {config.book_duration}ч.')
        else:
            bot.send_message(callback.message.chat.id, 'Данные устарели, попробуйте еще раз')
        return wait_command(callback.message)
    if not new_info_list:
        bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.id)
        bot.send_message(callback.message.chat.id, 'Данные устарели, попробуйте еще раз')
        return choose_hall(callback.message)
    buttons = [[]]
    markup = types.InlineKeyboardMarkup(row_width=config.row_width)
    for i in range(0, len(new_info_list), config.row_width):
        buttons.append([types.InlineKeyboardButton(text=str(num), callback_data=str(num))
                        for num in new_info_list[i:i + config.row_width]])
    for button in buttons:
        markup.add(*button)
    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.id, text=new_text, reply_markup=markup)


def get_callback_list_and_text(text, user_id):
    new_info_list = []
    new_text = ''
    if "зал" in text:
        db.write_user_parameter(user_id, "book_hall", text)
        new_info_list = [get_date(datetime.now(), i) for i in range(config.day_cnt)]
        new_text = 'Выбери дату'
    elif ("." in text) and (" " not in text):
        db.write_user_parameter(user_id, "book_date", text)
        new_info_list = [i for i in range(1, config.max_person_cnt+1)]
        new_text = 'Количество гостей'
    elif text.isdigit():
        db.write_user_parameter(user_id, "book_people_cnt", text)
        my_date = db.get_user_parameter(user_id, "book_date")
        my_hall = db.get_user_parameter(user_id, "book_date")
        my_people_cnt = text
        time_dict = google_api.get_sheet_dict(my_hall, my_people_cnt, my_date)
        today_day = (datetime.now()).strftime("%d.%m.%y")
        now = (datetime.now()).strftime('%H:%M')
        now = datetime.strptime(now, '%H:%M')
        for t in list(time_dict.keys()):
            tt = datetime.strptime(t, '%H:%M')
            if tt > now or str(today_day) != str(my_date):
                new_info_list.append(t)
        new_info_list.sort()
        new_text = 'Время'
    elif ":" in text:
        db.write_user_parameter(user_id, "book_time", text)
        my_hall, my_date, my_time, my_table, my_people_cnt = get_my_book(user_id)
        time_dict = google_api.get_sheet_dict(my_hall, my_people_cnt, my_date)
        if text in time_dict.keys():
            new_info_list = time_dict[text]
            new_text = 'Свободные столы на это время'
        else:
            new_text = 'Все столы заняты! Попробуйте выбрать другое время.'
    else:
        db.write_user_parameter(user_id, "book_table", text)
    return new_info_list, new_text


def check_dubl_message(message):
    current_time = datetime.now()
    last_datetime = CHAT_BY_DATETIME.get(message.chat.id)
    if not last_datetime:
        CHAT_BY_DATETIME[message.chat.id] = current_time
    else:
        delta_seconds = (current_time - last_datetime).total_seconds()
        CHAT_BY_DATETIME[message.chat.id] = current_time
        if delta_seconds < 2:
            return 1
    return 0


bot.infinity_polling()

