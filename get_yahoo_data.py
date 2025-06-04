import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import time

class YahooDataFetcher:
    def __init__(self, save_dir='data'):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def fetch_data(self, symbol, start_date=None, end_date=None, retry_count=3, retry_delay=5):
        """获取指定股票的历史数据
        
        Args:
            symbol (str): 股票代码
            start_date (str): 起始日期
            end_date (str): 结束日期
            retry_count (int): 重试次数
            retry_delay (int): 重试延迟（秒）
        """
        for attempt in range(retry_count):
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                return df
            except Exception as e:
                if "Rate limit" in str(e) and attempt < retry_count - 1:
                    print(f"遇到频率限制，等待{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                raise e
    
    def save_to_csv(self, symbol, df, start_date=None, end_date=None):
        """将数据保存为CSV文件
        
        Args:
            symbol (str): 股票代码
            df (pandas.DataFrame): 要保存的数据
            start_date (str): 起始日期，用于文件命名
            end_date (str): 结束日期，用于文件命名
        """
        if start_date is None:
            start_date = df.index[0].strftime('%Y%m%d')
        if end_date is None:
            end_date = df.index[-1].strftime('%Y%m%d')
            
        filename = f"{symbol}_{start_date}_{end_date}.csv"
        filepath = os.path.join(self.save_dir, filename)
        df.to_csv(filepath)
        print(f"数据已保存到: {filepath}")
    
    def get_stock_data(self, symbol, start_date=None, end_date=None):
        """获取并保存股票数据的主方法
        
        Args:
            symbol (str): 股票代码
            start_date (str): 起始日期，格式'YYYY-MM-DD'
            end_date (str): 结束日期，格式'YYYY-MM-DD'
        """
        try:
            df = self.fetch_data(symbol, start_date, end_date)
            if df.empty:
                print(f"未找到股票 {symbol} 的数据")
                return None
            
            self.save_to_csv(symbol, df, start_date, end_date)
            return df
        except Exception as e:
            print(f"获取数据时出错: {str(e)}")
            return None

# 使用示例
if __name__ == '__main__':
    fetcher = YahooDataFetcher()
    # 获取苹果公司2023年的股票数据
    df = fetcher.get_stock_data('AAPL', '2023-12-01', '2023-12-31')