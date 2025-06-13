import yfinance as yf
from setting import database_path

yf.set_config(proxy="http://127.0.0.1:7890")
# 获取 Apple 公司的股票数据
apple = yf.Ticker("AAPL")
 
# 获取最近 5 天的历史数据
hist = apple.history(period="5d")
 
# 打印数据
print(hist)