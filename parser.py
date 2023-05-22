import hashlib
import hmac
import time
import json
import urllib.request
from urllib.request import urlopen
import requests


PAIR_NAMES = ["BTC", "ETH", "LTC", "DASH", "XRP", "BCH"]


class PayeerParser():
    ts = int(round(time.time() * 1000))
    method = 'ticker'
    req = json.dumps({
        'ts': ts,
    })
    H = hmac.new(b'PCgFNfQB6WfhMuE0', digestmod=hashlib.sha256)
    H.update((method + req).encode('utf-8'))
    sign = H.hexdigest()

    headers = {
        'Content-Type': 'application/json',
        'API-ID': '1daecebc-b1ee-4174-99f9-b6ca09840762',
        'API-SIGN': sign
    }

    def print_prices(self):
        prices = self.get_all_prices()
        result = str(prices)
        result = result.replace(',', '$\n')
        result = result.replace('{', '')
        result = result.replace('}', '')
        result = result.replace("'", "")
        return result + "$"

    def get_all_prices(self):
        request = urllib.request.Request('https://payeer.com/api/trade/' + self.method,
                                         data=bytes(self.req.encode('utf-8')),
                                         headers=self.headers)

        response = json.loads(urlopen(request).read())
        pair_name = PAIR_NAMES
        prices = {}
        for i in pair_name:
            prices[i] = response['pairs'][i + "_USD"]['ask']
        return prices

    def get_price(self, pair_name):
        request = urllib.request.Request('https://payeer.com/api/trade/' + self.method,
                                         data=bytes(self.req.encode('utf-8')),
                                         headers=self.headers)

        response = json.loads(urlopen(request).read())
        print(time.asctime())
        return f"\n{pair_name}: {response['pairs'][pair_name]['ask']}$"


class KucoinParser():

    def print_prices(self):
        prices = self.get_all_prices()
        result = str(prices)
        result = result.replace(',', '$\n')
        result = result.replace('{', '')
        result = result.replace('}', '')
        result = result.replace("'", "")
        return result + "$"

    def get_price(self, to, from_l):
        price_list2 = requests.get(
            "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={}-{}".format(to, from_l)).json()
        # print(price_list2['data']['price'])
        return price_list2['data']['price']

    def get_all_prices(self):
        pair_name = PAIR_NAMES
        prices = {}
        for i in pair_name:
            prices[i] = self.get_price(i, "USDT")
        return prices


class BinanceParser():

    def print_prices(self):
        prices = self.get_all_prices()
        result = str(prices)
        result = result.replace(',', '$\n')
        result = result.replace('{', '')
        result = result.replace('}', '')
        result = result.replace("'", "")
        return result + "$"

    def get_all_prices(self):
        pair_name = PAIR_NAMES
        prices = {}
        for i in pair_name:
            prices[i] = self.get_price(i + "USDT")
        return prices

    def get_price(self, pair_name):
        url = "https://api.binance.com/api/v3/ticker/bookTicker"
        params = {
            'symbol': pair_name
        }
        r = requests.get(url, params=params).json()
        return float(r['bidPrice']) // 0.01 / 100


class Analytics():

    p = PayeerParser()
    k = KucoinParser()
    b = BinanceParser()

    def minMaxPrice(self, b: dict, p:dict, k:dict, coin:str):
        message = ""
        b = float(b[coin])
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
        binancePrices = self.b.get_all_prices()
        payeerPrices = self.p.get_all_prices()
        kucoinPrices = self.k.get_all_prices()

        for i in kucoinPrices.keys():
            if max(float(binancePrices[i]), float(payeerPrices[i]), float(kucoinPrices[i]))/min(float(binancePrices[i]), float(payeerPrices[i]), float(kucoinPrices[i])) > 1.01:
                return self.minMaxPrice(binancePrices, payeerPrices, kucoinPrices, i)
        return 0


