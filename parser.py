import hashlib
import hmac
import time
import json
import urllib.request
from urllib.request import urlopen
import requests
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

COINS_NAMES = ["BTC", "ETH", "LTC", "DASH", "XRP", "BCH"]


class Parser():

    @staticmethod
    def request_prices_from_payeer():
        ts = int(round(time.time() * 1000))
        method = 'ticker'
        req = json.dumps({
            'ts': ts,
        })
        H = hmac.new(b'PCgFNfQB6WfhMuE0', digestmod=hashlib.sha256)
        H.update((method + req).encode('utf-8'))
        sign = H.hexdigest()
        token = os.getenv("API_PAYEER_TOKEN")

        headers = {
            'Content-Type': 'application/json',
            'API-ID': token,
            'API-SIGN': sign
        }
        request = urllib.request.Request('https://payeer.com/api/trade/' + method,
                                         data=bytes(req.encode('utf-8')),
                                         headers=headers)
        response = json.loads(urlopen(request).read())
        return response

    def print_prices_from_payeer(self):
        prices = self.get_all_prices_from_payeer()
        result = str(prices).replace(',', '$\n').replace('{', '').replace('}', '').replace("'", "")
        return "Payeer:\n " + result + "$"

    def get_all_prices_from_payeer(self):
        response = self.request_prices_from_payeer()
        pair_name = COINS_NAMES
        prices = {}
        for i in pair_name:
            prices[i] = response['pairs'][i + "_USD"]['ask']
        return prices

    def get_price_from_payeer(self, pair_name):
        response = self.request_prices_from_payeer()
        print(time.asctime())
        return f"\n{pair_name}: {response['pairs'][pair_name]['ask']}$"

    def print_prices_from_kucoin(self):
        prices = self.get_all_prices_from_kucoin()
        result = str(prices).replace(',', '$\n').replace('{', '').replace('}', '').replace("'", "")
        return "Kucoin:\n " + result + "$"

    @staticmethod
    def get_price_from_kucoin(to, from_l):
        price_list2 = requests.get(
            "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={}-{}".format(to, from_l)).json()
        return price_list2['data']['price']

    def get_all_prices_from_kucoin(self):
        pair_name = COINS_NAMES
        prices = {}
        for i in pair_name:
            prices[i] = self.get_price_from_kucoin(i, "USDT")
        return prices

    def print_prices_from_binance(self):
        prices = self.get_all_prices_from_binance()
        result = str(prices).replace(',', '$\n').replace('{', '').replace('}', '').replace("'", "")
        return "Binance:\n " + result + "$"

    def get_all_prices_from_binance(self):
        pair_name = COINS_NAMES
        prices = {}
        for i in pair_name:
            prices[i] = self.get_price_from_binance(i + "USDT")
        return prices

    @staticmethod
    def get_price_from_binance(pair_name):
        url = "https://api.binance.com/api/v3/ticker/bookTicker"
        params = {
            'symbol': pair_name
        }
        r = requests.get(url, params=params).json()
        if pair_name != "XRPUSDT":
            return float(r['bidPrice']) // 0.01 / 100
        else:
            return float(r['bidPrice']) // 0.0001 / 10000

    @staticmethod
    def checkDiff(b: dict, p: dict, k: dict, coin: str):
        a = max(float(b[coin]), float(p[coin]), float(k[coin])) / min(
                float(b[coin]), float(p[coin]), float(k[coin]))
        if a > 1.01:
            return a
        return 0

    @staticmethod
    def minMaxPriceMessage(b: dict, p: dict, k: dict, coin: str):
        message = ""
        b: float = float(b[coin])
        p = float(p[coin])
        k = float(k[coin])
        if b == max(b, p, k):
            if p == min(p, k):
                message = f"Найдена связка.\n Покупка на Payeer {coin} по цене: {p}$ \n Продажа на Binance по цене: {b}$ \n Разница = {((b / p - 1) * 100) // 0.01 / 100}% "
            elif k == min(p, k):
                message = f"Найдена связка.\n Покупка на Kucoin {coin} по цене: {k}$ \n Продажа на Binance по цене: {b}$ \n Разница = {((b / k - 1) * 100) // 0.01 / 100}% "
        elif p == max(b, p, k):
            if b == min(b, k):
                message = f"Найдена связка.\n Покупка на Binance {coin} по цене: {b}$ \n Продажа на Payeer по цене: {p}$ \n Разница = {((p / b - 1) * 100) // 0.01 / 100}% "
            elif k == min(b, k):
                message = f"Найдена связка.\n Покупка на Kucoin {coin} по цене: {k}$ \n Продажа на Payeer по цене: {p}$ \n Разница = {((p / k - 1) * 100) // 0.01 / 100}% "
        else:
            if b == min(b, p):
                message = f"Найдена связка.\n Покупка на Binance {coin} по цене: {b}$ \n продажа на Kucoin по цене: {k}$ \n Разница = {((k / b - 1) * 100) // 0.01 / 100}% "
            elif p == min(b, p):
                message = f"Найдена связка.\n Покупка на Payeer {coin} по цене: {p}$ \n Продажа на Kucoin по цене: {k}$ \n Разница = {((k / p - 1) * 100) // 0.01 / 100}% "
        return message

    def print_message(self):
        message = "Не найдено выгодных сделок"
        binancePrices = self.get_all_prices_from_binance()
        payeerPrices = self.get_all_prices_from_payeer()
        kucoinPrices = self.get_all_prices_from_kucoin()
        maxDiff = 0

        for coin in kucoinPrices.keys():
            diff = self.checkDiff(b=binancePrices, p=payeerPrices, k=kucoinPrices, coin=coin)
            if diff > 1.01 and diff > maxDiff:
                maxDiff = diff
                message = self.minMaxPriceMessage(b=binancePrices, p=payeerPrices, k=kucoinPrices, coin=coin)
        return message


