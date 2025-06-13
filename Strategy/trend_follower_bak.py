from backtesting import Strategy, Backtest
from setting import database_path, logger
import pandas as pd
import sqlite3


class TrendFollower(Strategy):

    def init(self):
        logger.debug("test if init function")
        self.selected = None
        self.init_stock_pool()

    def init_stock_pool(self):
        # order by volume select 100 and price > 1 hkd
        self.selected = self.data.df[self.data.df['Close'] > 1].sort_values(by='amount', ascending=False).iloc[:100, 0].reset_index()[
            'symbol']
        return self.selected

    def next(self):
        # 将创新高的股票 加入待买入列表
        logger.debug("test next function")

def query_data(start_dt="2024-01-01", end_dt="2024-12-31"):
    con = sqlite3.connect(database=database_path)
    logger.debug(database_path)
    with sqlite3.connect(database=database_path) as con:
        # OHLCV
        stock_sql_str = "select t.symbol ,t.Open,t.High ,t.Low ,t.Close,t.Volume ,t.amount,t.date  from stock_data t where t.date between '%s' and '%s' order by t.date" % (
            start_dt, end_dt)
        data = pd.read_sql_query(
            sql=stock_sql_str,
            con=con,
            index_col='date',
            parse_dates=['date']
        )
    return data


def run():
    data = query_data()
    logger.debug('query data:%s ' % str(data.shape))
    bt = Backtest(
        data=data[data['symbol']=='00001'],
        strategy=TrendFollower,
        cash=10000,
        commission=0.0015
    )
    stats = bt.run()

    logger.info('trade log:/n %s' % stats['_trades'])
    bt.plot()


if __name__ == "__main__":
    logger.info('start run')
    run()
