import telebot
import os
import time
import random
from telebot import types

from config import token,database_name
from utils import get_rows_count,generate_markup,set_user_game,get_answer_for_user,finish_user_game,count_rows
from SQLighter import SQLighter

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['game'])
def game(message):
    # Подключаемся к БД
    db_worker = SQLighter(database_name)
    # Получаем случайную строку из БД
    row = db_worker.select_single(random.randint(1, get_rows_count()))
    # Формируем разметку
    markup = generate_markup(row[2], row[3])
    # Отправляем аудиофайл с вариантами ответа

    audio = open(r'./music/'+str(row[1]), 'rb')
    bot.send_audio(message.chat.id, audio,reply_markup=markup, duration=20)
    audio.close()

    # bot.send_voice(message.chat.id, './music/'+str(row[1]), reply_markup=markup, duration=20)
    # Включаем "игровой режим"
    set_user_game(message.chat.id, row[2])
    # Отсоединяемся от БД
    db_worker.close()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    # Если функция возвращает None -> Человек не в игре
    answer = get_answer_for_user(message.chat.id)
    # Как Вы помните, answer может быть либо текст, либо None
    # Если None:
    if not answer:
        bot.send_message(message.chat.id, 'Чтобы начать игру, выберите команду /game')
    else:
        # Уберем клавиатуру с вариантами ответа.
        keyboard_hider = types.ReplyKeyboardRemove()
        # Если ответ правильный/неправильный
        if message.text == answer:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Увы, Вы не угадали. Попробуйте ещё раз!', reply_markup=keyboard_hider)
        # Удаляем юзера из хранилища (игра закончена)
        finish_user_game(message.chat.id)


@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('music/'):
        if file.split('.')[-1] == 'ogg':
            f = open("music/"+file, 'rb')
            res = bot.send_voice(message.chat.id, f, None)
            print(res)
        time.sleep(3)


if __name__ == '__main__':
    count_rows()
    random.seed()
    bot.infinity_polling()