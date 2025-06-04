import tushare as ts
import pandas as pd
from datetime import datetime
import os
import time

#97d18396ef6968d71f7a93c85b7eca5ca15321bd781212211effaedf

class TushareDataFetcher:
    def __init__(self, token, save_dir='data'):
        """初始化Tushare数据获取器
        
        Args:
            token (str): Tushare的API token，需要在官网注册获取
            save_dir (str): CSV文件保存目录，默认为'data'
        """
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        # 设置Tushare Token
        ts.set_token(token)
        self.pro = ts.pro_api()
    
    def fetch_data(self, symbol, start_date=None, end_date=None, retry_count=3):
        """获取指定股票的历史数据
        
        Args:
            symbol (str): 股票代码，例如'000001.SZ'为平安银行
            start_date (str): 起始日期，格式'YYYYMMDD'
            end_date (str): 结束日期，格式'YYYYMMDD'
            retry_count (int): 重试次数
        
        Returns:
            pandas.DataFrame: 包含历史价格数据的DataFrame
        """
        for attempt in range(retry_count):
            try:
                df = self.pro.daily(
                    ts_code=symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                # 按照日期升序排序
                df = df.sort_values('trade_date')
                return df
            except Exception as e:
                if attempt < retry_count - 1:
                    print(f"获取数据失败，{retry_count-attempt-1}次重试机会...")
                    time.sleep(1)  # 等待1秒后重试
                    continue
                raise e
    
    def save_to_csv(self, symbol, df, start_date=None, end_date=None):
        """将数据保存为CSV文件
        
        Args:
            symbol (str): 股票代码
            df (pandas.DataFrame): 要保存的数据
            start_date (str): 起始日期
            end_date (str): 结束日期
        """
        if df is None or df.empty:
            print(f"没有数据可保存：{symbol}")
            return
            
        if start_date is None:
            start_date = df['trade_date'].min()
        if end_date is None:
            end_date = df['trade_date'].max()
            
        filename = f"{symbol}_{start_date}_{end_date}.csv"
        filepath = os.path.join(self.save_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"数据已保存到: {filepath}")
    
    def get_stock_list(self):
        """获取股票列表
        
        Returns:
            pandas.DataFrame: 包含所有股票基本信息的DataFrame
        """
        try:
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            return df
        except Exception as e:
            print(f"获取股票列表失败：{str(e)}")
            return None
    
    def get_stock_data(self, symbol, start_date=None, end_date=None):
        """获取并保存股票数据的主方法
        
        Args:
            symbol (str): 股票代码
            start_date (str): 起始日期，格式'YYYYMMDD'
            end_date (str): 结束日期，格式'YYYYMMDD'
        """
        try:
            # 如果输入的是不带后缀的代码，尝试自动添加后缀
            if '.' not in symbol:
                if symbol.startswith('6'):
                    symbol = f"{symbol}.SH"
                else:
                    symbol = f"{symbol}.SZ"
            
            df = self.fetch_data(symbol, start_date, end_date)
            if df is not None and not df.empty:
                self.save_to_csv(symbol, df, start_date, end_date)
            return df
        except Exception as e:
            print(f"获取数据时出错: {str(e)}")
            return None

# 使用示例
if __name__ == '__main__':
    # 在使用前需要设置token
    token = '97d18396ef6968d71f7a93c85b7eca5ca15321bd781212211effaedf'  # 替换为你的token
    fetcher = TushareDataFetcher(token)
    
    # 获取单只股票的数据
    df = fetcher.get_stock_data('000001', '20230801', '20231130')
    
    # 获取股票列表
    stock_list = fetcher.get_stock_list()
    if stock_list is not None:
        print(f"共获取到{len(stock_list)}只股票信息")