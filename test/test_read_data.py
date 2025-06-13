import pandas as pd
import sqlite3
from setting import database_path, logger


class dataobject(object):
    def __init__(self, data):
        self.df = data


def query_data(start_dt="20240101", end_dt="20241231"):
    con = sqlite3.connect(database=database_path)
    logger.debug(database_path)
    with sqlite3.connect(database=database_path) as con:
        # OHLCV
        stock_sql_str = "select t.stock_id ,t.open,t.high ,t.low ,t.close,t.volume ,t.date  from stock_data t where t.date between '%s' and '%s'" % (
            start_dt, end_dt)
        data = pd.read_sql_query(
            sql=stock_sql_str,
            con=con,
            index_col='date',
            parse_dates=['date']
        )
    return data


def init_stock_pool(stock_data_df):
    # order by volume select 100 and price > 1 hkd
    data = dataobject(stock_data_df)
    selected = data.df[data.df['close'] > 1].sort_values(by='amount', ascending=False).iloc[:100, 0].reset_index()[
        'stock_id']
    logger.debug(selected.shape)


if __name__ == "__main__":
    init_stock_pool(query_data())
