from urllib.request import urlopen
import json
from yfinance import Ticker

def is_prime(n: int) -> bool:
    if n==2 or n==3: return True
    if n%2==0 or n<2: return False
    for i in range(3, int(n**0.5)+1, 2):
        if n%i==0:
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
    return stock_info['regularMarketPrice'], stock_info['regularMarketPreviousClose']
