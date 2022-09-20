from random import randint
import telebot
from telebot import types
from datetime import datetime
import requests
from utils import *
import re
import json

print(f'----------------- Bot started at {datetime.now()} -----------------')

API_TOKEN = "5776672843:AAHoH2Z2rhTXJcGr0XZBbrtt5xMyTfcR-_o"
bot = telebot.TeleBot(API_TOKEN)

def get_record_chatid_map() -> dict:
    with open('username_chatid_map.json', 'r') as f:
        return json.load(f)

def save_record_chatid_map(username_to_chat_id) -> None:
    with open('username_chatid_map.json', 'w') as fj:
        json.dump(username_to_chat_id, fj)

def record_chat_id(message) -> bool:
    username_to_chat_id = get_record_chatid_map()
    if message.from_user.username not in username_to_chat_id:
        username_to_chat_id[message.from_user.username] = message.chat.id
        save_record_chatid_map(username_to_chat_id)
        return True
    return False

def chid(message):
    '''
    Returns message's chat id
    '''
    return message.chat.id

def log_message(message, extra=''):
    if (mct := message.content_type) == 'text':
        to_log = f'{datetime.now()}\t{message.from_user.username}\ttext\t[{message.text}] {extra}'
    elif mct == 'photo':
        to_log = f'{datetime.now()}\t{message.from_user.username}\tphoto\t[{message.text}]\tid={message.photo[0].file_id}'
    elif mct == 'document':
        to_log = f'{datetime.now()}\t{message.from_user.username}\tdocument\t[{message.text}]\tid={message.document.file_id}'
    elif mct == 'voice':
        to_log = f'{datetime.now()}\t{message.from_user.username}\tvoice\t[{message.text}]\tid={message.voice.file_id}'
    elif mct == 'contact':
        to_log = f'{datetime.now()}\t{message.from_user.username}\tcontact\t[{message.text}]\tphone={message.contact.phone_number}\tuser_id={message.contact.user_id}'
    with open('log.txt', 'a+') as f:
        print(to_log, file=f)



# basic commands

@bot.message_handler(commands=['start'])
def send_welcome(message):
    start_text = '\n'.join([
        f'Hello, {message.from_user.first_name}!',
        'Type /help to see the command list.'
    ])
    bot.reply_to(message, start_text)
    log_message(message)

@bot.message_handler(commands=['help'])
def send_help(message):
    log_message(message)
    help_text = '\n'.join([
        'Try these commands:',
        '"/prime <number>" to test if the entered number is a prime;',
        '"/random <a> <b>" to get a random integer from [a, b];',
        '"/advice" to get a random advice or "/advice <keyword>" to get some advice with a given key word;',
        '"/stocks <ticker>" to get a given stock\'s price.'
    ])
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['sub'])
def sub(message):
    log_message(message)
    if record_chat_id(message):
        bot.send_message(chid(message), 'You will get a notification soon!')
    else:
        bot.send_message(chid(message), 'You are already subscribed!')

@bot.message_handler(commands=['notify'])
def notify(message):
    log_message(message)
    if chid(message) == 409474295:
        user_chat_ids = get_record_chatid_map()
        for username, chat_id in user_chat_ids.items():
            bot.send_message(chat_id, f'Notification to {username}!')
        bot.send_message(chid(message), f'{" ".join(user_chat_ids.keys())} have been notified.')
    else:
        bot.send_message(chid(message), f'Sorry, you need to be an admin :(')


# commands with keyboards

@bot.message_handler(commands=['keyboard'])
def get_keyboard_type(message):
    sent = bot.send_message(chid(message), 'Enter a keyboard type (inline/reply/info):')
    bot.register_next_step_handler(sent, start_keyboard)
def start_keyboard(message):
    if message.text == 'inline':
        print('inline')
        kb = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton('Btn1', url='google.com')
        btn2 = types.InlineKeyboardButton('Btn2', callback_data='btn2')
        btn3 = types.InlineKeyboardButton('Btn3', callback_data='btn3')
        kb.add(btn1, btn2, btn3) 
        sent = bot.send_message(chid(message), 'Choose a button:', reply_markup=kb)
    elif message.text == 'reply':
        print('reply')
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('Dummy1')
        btn2 = types.KeyboardButton('Dummy2')
        kb.add(btn1, btn2)
        sent = bot.send_message(chid(message), 'Choose a button:', reply_markup=kb)
        bot.register_next_step_handler(sent, process_reply_buttons)
    elif message.text == 'info':
        print('info')
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Contacts', request_contact=True)
        btn2 = types.KeyboardButton('Location', request_location=True)
        kb.add(btn1, btn2)
        sent = bot.send_message(chid(message), 'Choose a button:', reply_markup=kb)
    
def process_reply_buttons(message):
    bot.send_message(chid(message), f'You pressed {message.text}', reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda cb: cb.data)
def process_inline_buttons(callback):
    if callback.data == 'btn2':
        bot.send_message(chid(callback.message), f'You chose Btn2')
    elif callback.data == 'btn3':
        bot.send_message(chid(callback.message), f'You chose Btn3')

# commands with arguments

prime_pattern = r'/prime +(\d+)$'
@bot.message_handler(commands=['prime'])
def is_prime_number(message):
    log_message(message)
    if (m := re.compile(prime_pattern).match(message.text)):
        num, = m.groups()
        not_ = 'NOT ' if not is_prime(int(num)) else ''
        ret_text = f'{num} is {not_}a prime number'
        bot.reply_to(message, ret_text)
    else:
        bot.send_message(chid(message), 'Wrong format.')

rnd_number_pattern = r'/random +(\d+) +(\d+)$'
@bot.message_handler(commands=['random'])
def get_random_number(message):
    log_message(message)
    if (m := re.compile(rnd_number_pattern).match(message.text)):
        a, b = m.groups()
        ret_text = f'Your number is {randint(int(a), int(b))}'
        bot.reply_to(message, ret_text)
    else:
        bot.send_message(chid(message), 'Wrong format.')

advice_pattern = r'/advice +(\w+)'
@bot.message_handler(commands=['advice'])
def get_advice(message):
    if (m := re.compile(advice_pattern).match(message.text)):
        word, = m.groups()
        advice = get_list_of_advice(word)
        log_message(message)
    else:
        advice = get_random_advice()
        log_message(message, extra=advice)
    bot.send_message(chid(message), advice)

stocks_pattern = r'/stocks +(\w+)'
@bot.message_handler(commands=['stocks'])
def stocks(message):
    log_message(message)
    if (m := re.compile(stocks_pattern).match(message.text)):
        ticker, = m.groups()
        regular_price, close_price = get_stocks_price(ticker)
        if regular_price:
            bot.send_message(chid(message), f'Regular market price: {regular_price}\nClosing price: {close_price}')
        else:
            bot.send_message(chid(message), f'Unknown ticker: {ticker}.')
    else:
        bot.send_message(chid(message), 'Wrong format.')

req_photo_by_id_pattern = r'/photo +(.+)$'
@bot.message_handler(commands=['photo'])
def get_photo_by_id(message):
    log_message(message)
    if (m := re.compile(req_photo_by_id_pattern).match(message.text)):
        photo_id, = m.groups()
        print(photo_id)
        try:
            bot.send_photo(chid(message), photo_id, 'photo by id')
        except Exception as e:
            print('No such photo', e)
            bot.reply_to(message, 'No photo with this id')
    else:
        bot.send_message(chid(message), 'Wrong format.')

req_file_by_id_pattern = r'/file +(.+)$'
@bot.message_handler(commands=['file'])
def get_file_by_id(message):
    log_message(message)
    if (m := re.compile(req_file_by_id_pattern).match(message.text)):
        file_id, = m.groups()
        print(file_id)
        try:
            bot.send_document(chid(message), file_id, 'file by id')
        except Exception as e:
            print('No such file', e)
            bot.reply_to(message, 'No file with this id')
    else:
        bot.send_message(chid(message), 'Wrong format.')

download_pattern = r'/download +(.+)$'
@bot.message_handler(commands=['download'])
def get_file_by_id(message):
    log_message(message)
    if (m := re.compile(download_pattern).match(message.text)):
        file_id, = m.groups()
        print(file_id)
        try:
            file_info = bot.get_file(file_id)
            url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}'
            print(url)
            file = requests.get(url)
            with open(file_info.file_path, 'wb') as fw:
                fw.write(file.content)
        except Exception as e:
            print('No such file', e)
            bot.reply_to(message, 'No file with this id')
    else:
        bot.send_message(chid(message), 'Wrong format.')

# by content type

@bot.message_handler(content_types=['photo'])
def process_photo(message):
    log_message(message)
    print('photo', message.photo[0])
    bot.send_message(chid(message), f'Got a photo of size {message.photo[0].file_size} bytes')
    
@bot.message_handler(content_types=['document'])
def process_file(message):
    log_message(message)
    print('document', message.document)
    bot.send_message(chid(message), f'Got a document {message.document.file_name} of size {message.document.file_size} bytes')

@bot.message_handler(content_types=['voice'])
def process_voice(message):
    log_message(message)
    print('voice', message.voice)
    bot.send_message(chid(message), f'Got a voice message ({message.voice.duration} sec) of size {message.voice.file_size} bytes')

@bot.message_handler(content_types=['contact'])
def process_contact(message):
    log_message(message)
    mc = message.contact
    with open('contacts.csv', 'a+') as f:
        print(mc.first_name, mc.phone_number, mc.user_id, file=f, sep=',')
    bot.send_message(chid(message), 'Contact successfully received!', reply_markup=types.ReplyKeyboardRemove())

# from the local dir
@bot.message_handler(commands=['getphoto'])
def some_photo(message):
    log_message(message)
    print('sending a photo')
    with open('photos/test1.png', 'rb') as photo:
        bot.send_photo(chid(message), photo)

# else:
@bot.message_handler(func=lambda message: message.text.startswith('/'))
def echo_command(message):
    log_message(message)
    bot.send_message(chid(message), 'Sorry, I don\'t know this command. Try typing /help')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    log_message(message)
    bot.send_message(chid(message), 'What sort of gibberish is this?')

bot.infinity_polling()
