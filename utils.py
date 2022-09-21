from urllib.request import urlopen
import json
from yfinance import Ticker
from datetime import datetime

def chid(message):
    '''
    Returns message's chat id
    '''
    return message.chat.id

def log_message(message, extra=''):
    if (mct := message.content_type) == 'text':
        to_log = f'{datetime.now()}\t{message.from_user.username}({message.chat.id})\ttext\t[{message.text}] {extra}'
    elif mct == 'photo':
        to_log = f'{datetime.now()}\t{message.from_user.username}({message.chat.id})\tphoto\t[{message.text}]\tid={message.photo[0].file_id}'
    elif mct == 'document':
        to_log = f'{datetime.now()}\t{message.from_user.username}({message.chat.id})\tdocument\t[{message.text}]\tid={message.document.file_id}'
    elif mct == 'voice':
        to_log = f'{datetime.now()}\t{message.from_user.username}({message.chat.id})\tvoice\t[{message.text}]\tid={message.voice.file_id}'
    elif mct == 'contact':
        to_log = f'{datetime.now()}\t{message.from_user.username}({message.chat.id})\tcontact\t[{message.text}]\tphone={message.contact.phone_number}\tuser_id={message.contact.user_id}'
    with open('log.txt', 'a+', encoding='utf-8') as f:
        print(to_log, file=f)

def log(func):
    def wrapper_func(msg):
        log_message(msg)
        return func(msg)
    return wrapper_func


def get_record_chatid_map() -> dict:
    with open('username_chatid_map.json', 'r') as f:
        return json.load(f)

def save_record_chatid_map(username_to_chat_id) -> None:
    with open('username_chatid_map.json', 'w') as fj:
        json.dump(username_to_chat_id, fj)

def record_chat_id_entry(message) -> bool:
    username_to_chat_id = get_record_chatid_map()
    if message.from_user.username not in username_to_chat_id:
        username_to_chat_id[message.from_user.username] = message.chat.id
        save_record_chatid_map(username_to_chat_id)
        return True
    return False

def delete_chat_id_entry(message) -> bool:
    username_to_chat_id = get_record_chatid_map()
    if message.from_user.username in username_to_chat_id:
        del username_to_chat_id[message.from_user.username]
        save_record_chatid_map(username_to_chat_id)
        return True
    return False


def is_prime(n: int) -> bool:
    if n == 2 or n == 3: return True
    if n % 2 == 0 or n < 2: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_random_advice() -> str:
    url = 'https://api.adviceslip.com/advice'
    with urlopen(url) as url:
        data = json.load(url)
    return data['slip']['advice']

def get_list_of_advice(key_word) -> list[str]:
    url = f'https://api.adviceslip.com/advice/search/{key_word}'
    with urlopen(url) as url:
        data : dict = json.load(url)
    slips = data.get('slips', None)
    if slips:
        if len(slips) > 20:
            slips = slips[:20]
        return '\n'.join((s['advice'] for s in slips))
    return f'No advice for {key_word} :('

def get_stocks_price(ticker):
    stock = Ticker(ticker)
    stock_info = stock.info
    return stock_info['regularMarketPrice'], stock_info['regularMarketPreviousClose'], stock_info['longName']
