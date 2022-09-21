import telebot
from telebot import types
from utils import *
from random import randint
import requests
import re

print(f'----------------- Bot started at {(t1:=datetime.now())} -----------------')

with open('api_token.txt', 'r') as f:
    API_TOKEN = f.read()

bot = telebot.TeleBot(API_TOKEN)


# basic commands

@bot.message_handler(commands=['start'])
@log
def send_welcome(message):
    start_text = '\n'.join([
        f'Hello, {message.from_user.first_name}!',
        'Type /help to see the command list.'
    ])
    bot.reply_to(message, start_text)

@bot.message_handler(commands=['help'])
@log
def send_help(message):
    help_text = '\n'.join([
        'Try these commands:',
        '"/prime <number>" to test if the entered number is a prime;',
        '"/random <a> <b>" to get a random integer from [a, b];',
        '"/advice" to get a random advice or "/advice <keyword>" to get some advice with a given key word;',
        '"/stocks <ticker>" to get a given stock\'s price;',
        '"/keyboard";',
        '"/sub" or "/unsub"'
    ])
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['sub'])
@log
def sub(message):
    if record_chat_id_entry(message):
        bot.send_message(chid(message), 'You have just subscribed!')
    else:
        bot.send_message(chid(message), 'You are already subscribed!')

@bot.message_handler(commands=['unsub'])
@log
def sub(message):
    if delete_chat_id_entry(message):
        bot.send_message(chid(message), 'You have successfully unsubscribed!')
    else:
        bot.send_message(chid(message), 'You are not subscribed yet!')

@bot.message_handler(commands=['notify'])
@log
def notify(message):
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
@log
def is_prime_number(message):
    if (m := re.compile(prime_pattern).match(message.text)):
        num, = m.groups()
        not_ = 'NOT ' if not is_prime(int(num)) else ''
        ret_text = f'{num} is {not_}a prime number'
        bot.reply_to(message, ret_text)
    else:
        bot.send_message(chid(message), 'Wrong format. Try "/prime 23"')

rnd_number_pattern = r'/random +(\d+) +(\d+)$'
@bot.message_handler(commands=['random'])
@log
def get_random_number(message):
    if (m := re.compile(rnd_number_pattern).match(message.text)):
        a, b = m.groups()
        ret_text = f'Your number is {randint(int(a), int(b))}'
        bot.reply_to(message, ret_text)
    else:
        bot.send_message(chid(message), 'Wrong format. Try "/random 1 10"')

advice_pattern = r'/advice +(\w+)'
@bot.message_handler(commands=['advice'])
# log_message function has an extra argument => no decorator here
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
@log
def stocks(message):
    if (m := re.compile(stocks_pattern).match(message.text)):
        ticker, = m.groups()
        try:
            regular_price, close_price, name = get_stocks_price(ticker)
            bot.send_message(chid(message), f'{name}\nRegular market price: {regular_price}\nClosing price: {close_price}')
        except KeyError as e:
            bot.send_message(chid(message), f'Unknown ticker: {ticker}.')
            print(e)
    else:
        bot.send_message(chid(message), 'Wrong format. Try "/stocks aapl"')

req_photo_by_id_pattern = r'/photo +(.+)$'
@bot.message_handler(commands=['photo'])
@log
def get_photo_by_id(message):
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
@log
def get_file_by_id(message):
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
@log
def get_file_by_id(message):
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
@log
def process_photo(message):
    print('photo', message.photo[0])
    bot.send_message(chid(message), f'Got a photo of size {message.photo[0].file_size} bytes')
    
@bot.message_handler(content_types=['document'])
@log
def process_file(message):
    print('document', message.document)
    bot.send_message(chid(message), f'Got a document {message.document.file_name} of size {message.document.file_size} bytes')

@bot.message_handler(content_types=['voice'])
@log
def process_voice(message):
    print('voice', message.voice)
    bot.send_message(chid(message), f'Got a voice message ({message.voice.duration} sec) of size {message.voice.file_size} bytes')

@bot.message_handler(content_types=['contact'])
@log
def process_contact(message):
    mc = message.contact
    with open('contacts.csv', 'a+') as f:
        print(mc.first_name, mc.phone_number, mc.user_id, file=f, sep=',')
    bot.send_message(chid(message), 'Contact successfully received!', reply_markup=types.ReplyKeyboardRemove())

# from the local dir
@bot.message_handler(commands=['getphoto'])
@log
def some_photo(message):
    print('sending a photo')
    with open('photos/test1.png', 'rb') as photo:
        bot.send_photo(chid(message), photo)

# else:
@bot.message_handler(func=lambda message: message.text.startswith('/'))
@log
def echo_command(message):
    bot.send_message(chid(message), f'Unknown command: {message.text}. Try typing /help')

@bot.message_handler(func=lambda message: True)
@log
def echo_all(message):
    bot.send_message(chid(message), 'What sort of gibberish is this?')

bot.infinity_polling()

print(f'----------------- Bot shut down at {(t2:=datetime.now())} -----------------')
print('running time:', t2 - t1)