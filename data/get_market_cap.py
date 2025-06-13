import logging

import yfinance as yf

yf.set_config(proxy="http://127.0.0.1:7890")

data = yf.Ticker('00001.HK')
logging.INFO('APPLE market cap : %d'% data.fast_info.shares)