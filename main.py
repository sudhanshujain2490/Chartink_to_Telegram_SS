import logging
import os
from datetime import datetime as dt
from selenium import webdriver
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.common import keys
from selenium.webdriver.common.action_chains import ActionChains

import pandas as pd
import pytz
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

log = logging.getLogger(__name__)
# NOTE while creating date objects you can use zone info which is very helpful when you are running scripts on outside India location
zone = pytz.timezone('Asia/Kolkata')

import telepot

apiToken = '5891020797:AAHqKr2wfppR-C2gD53Gouay8gFHcs0kMQQ'
chatID = '-1001754989816' #'750877200'
apiURL = f'https://api.telegram.org/bot{apiToken}/sendPhoto'


def get_stocks():
    with requests.Session() as s:
        scanner_url = 'https://chartink.com/screener/vishal-mehta-mean-reversion'
        r = s.get(scanner_url)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf = soup.select_one("[name='csrf-token']")['content']
        s.headers['x-csrf-token'] = csrf

        process_url = 'https://chartink.com/screener/process'

        # payload = {
        #     'scan_clause': '( {57960} ( ( {cash} ( latest close > 3 days ago max ( 20 , latest high ) and 1 day ago  close <= 4 days ago  max ( 20 , latest high ) and 4 days ago high < 3 days ago max ( 20 , latest high ) and latest volume > latest sma ( volume,20 ) and latest close >= monthly "(1 candle ago high + 1 candle ago low + 1 candle ago close / 3)" and latest close >= monthly "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" and 1 day ago close < monthly "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" ) ) ) ) '
        # }

        payload = {
            'scan_clause': '( {33489} ( latest close > latest ema ( latest close , 11 ) and 1 day ago close < latest ema ( latest close , 11 ) and latest close > latest ema ( latest close , 2 ) and 1 day ago close < latest ema ( latest close , 2 ) and latest volume > latest ema ( latest volume , 20 ) ) ) '
        }
        # payload = {
        #     'scan_clause': '( {cash} ( latest close > 1 day ago max ( 60 , latest high ) and latest close > latest open and latest close > 1 day ago close and latest volume >= 1 day ago volume * 3 and 1 day ago ema ( latest volume , 50 ) < latest sma ( latest volume , 50 ) + ( latest sma ( latest volume , 50 ) * 0.5 ) and 1 day ago ema ( latest volume , 50 ) > latest sma ( latest volume , 50 ) ) ) '
        # }

        # payload = {
        #     # NOTE Vishal Mehta Mean Reversion Selling - Place Limit Order at 1% of Latest Close Price 3% SL and 6% Target Exit all positions at 3PM
        #     'scan_clause': '( {cash} ( latest close > latest sma( close, 200 ) and latest rsi( 2 ) > 50 and '\
        #     'latest close > 1 day ago close * 1.03 and latest close > 200 and latest close < 5000 and latest close > ( 4 days ago close * 1.0 ) ) ) '
        # }

        r = s.post(process_url, data=payload)
        df = pd.DataFrame()
        for item in r.json()['data']:
            df = df.append(item, ignore_index=True)
        # NOTE Sorting done by ascending price so that stock with less price can be purchased before
        # Costly stocks may be rejected if there is no capital
        df.sort_values(by=['close'], inplace=True)
        df.drop('sr', axis=1, inplace=True)
        df.reset_index(inplace=True)
        df.drop('index', axis=1, inplace=True)

        print(f'number of stocks :: {len(df)}')
        if len(df) > 10:
            print('returning only first 10 stocks')
            df = df.head(10)
        return df


if __name__ == "__main__":
    # global kite

    begin_time = dt.now(tz=zone)
    print(begin_time)

    stocks = get_stocks()


    for i in stocks['nsecode']:

        # URL of website
        url = "https://in.tradingview.com/chart/?symbol=" + str(i)
        print(url)

        # Here Chrome will be used
        driver = webdriver.Firefox()
        print('firefox check')

        # create action chain object
        action = ActionChains(driver)
        print('driver check')

        # Opening the website
        driver.get(url)
        print('Opening the website')
        sleep(5)
        driver.maximize_window()
        sleep(2)
        action.send_keys(Keys.ESCAPE).perform()
        sleep(2)
        action.key_down(Keys.SHIFT).send_keys('f').key_up(Keys.SHIFT).perform()
        sleep(2)
        driver.save_screenshot(str(i) + '.png')
        driver.quit()

        bot = telepot.Bot(apiToken)
        print(bot.getMe())
        # bot.sendPhoto(chatID, open(str(i) + '.png', 'rb'), url)
        bot.sendDocument(chatID, open(str(i) + '.png', 'rb'), url)
        print('photo send....')
        img_name = str(i) + '.png'

        os.remove(img_name)

        print("end...")
