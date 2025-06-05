from pathlib import Path
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
from loguru import logger

import pandas as pd

data_path = Path("data")
data_file = data_path.joinpath("00001.csv")
data_csv_df = pd.read_csv(data_file, encoding='GBK')

data_df = pd.DataFrame(
    data=data_csv_df.loc[:, ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量(股)']]).rename(
    columns={'开盘价': 'Open', '最高价': 'High', '最低价': 'Low', '收盘价': 'Close', '成交量(股)': 'Volume',
             '日期': 'Date'})
data_df['Date'] =  pd.to_datetime(data_df['Date'])
data_df = data_df.set_index('Date')
logger.info('data:\n%s' % data_df.tail())
logger.info('data:\n%s' % data_df.dtypes)

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

class TestStrategy(Strategy):
    n1 = 5
    n2 = 15
    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2,self.sma1):
            self.position.close()
            self.sell()

if __name__ == '__main__':
    bt = Backtest(
        data=data_df,
        strategy=TestStrategy,
        cash=10000,
        commission=0.0015
    )
    stats = bt.run()

    logger.info('trade log:/n %s'% stats['_trades'])
    # bt.plot()