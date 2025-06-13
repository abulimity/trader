from setting import logger, database_path
from CommInfo import LBCommInfo
import backtrader as bt
import backtrader.feeds as btfeeds
import datetime
import sqlite3
import pandas as pd


class TrendFollower(bt.Strategy):
    params = (
        # ('long_period', 25),
        # ('short_period', 20),
    )

    def __init__(self):
        # self.long_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.long_period)
        # self.short_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.short_period)
        self.dataclose = self.datas[0].close
        self.order = None

        self.prenext_count = 0
        self.nextstart_count = 0
        self.next_count = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                logger.info(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            elif order.issell():
                logger.info('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                            (order.executed.price,
                             order.executed.value,
                             order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            logger.info("trade_date:%s,Order Canceled/Margin/Rejected:%.2f" % (
                self.datas[0].datetime.date(0), self.dataclose[0]))

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        logger.info('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                    (trade.pnl, trade.pnlcomm))

    def prenext(self):
        self.prenext_count += 1
        logger.debug("prenext process %d times. trade_date:%s" % (self.prenext_count, self.datas[0].datetime.date(0)))
        top100_order_by_amount = """select symbol from stock_data t where t.date = '%s' order by amount desc limit 100""" % (
            self.datas[0].datetime.date(0))
        logger.info("top100_order_by_amount:%s" % top100_order_by_amount)

    def nextstart(self):
        self.nextstart_count += 1
        logger.info(
            "nextstart process %d times. trade_date:%s" % (self.nextstart_count, self.datas[0].datetime.date(0)))

    def next(self):
        self.next_count += 1
        logger.debug("next process %d times. trade_date:%s" % (self.prenext_count, self.datas[0].datetime.date(0)))
        top100_order_by_amount = """select symbol from stock_data t where t.date = '%s' order by amount desc limit 100""" % (
            self.datas[0].datetime.date(0))
        with sqlite3.connect(database=database_path) as con:
            data = pd.read_sql_query(
                sql=top100_order_by_amount,
                con=con,
                index_col='date',
                parse_dates=['date']
            )
        return data
        logger.info("top100_order_by_amount:%s" % top100_order_by_amount)

        # if self.order:
        #     return

        # if not self.position:

        #     if self.dataclose[0] > self.sma[0]:
        #         logger.info("trade_date:%s,BUY CREATE:%.2f" % (self.datas[0].datetime.date(0), self.dataclose[0]))
        #         self.order = self.buy()
        # else:
        #     if self.dataclose[0] < self.sma[0]:
        #         logger.info("trade_date:%s,SELL CREATE:%.2f" % (self.datas[0].datetime.date(0), self.dataclose[0]))
        #         self.order = self.sell()

    def strat(self):
        logger.info('start call')

    def stop(self):
        logger.info('stop call')


def query_data(symbol=None, start_dt="2024-01-01", end_dt="2024-12-31"):
    logger.debug(database_path)
    if symbol is not None:
        stock_sql_str = "select t.symbol ,t.Open,t.High ,t.Low ,t.Close,t.Volume ,t.amount,t.date  from stock_data t where t.symbol = '%s' and  t.date between '%s' and '%s' order by t.date" % (
            symbol, start_dt, end_dt)
    else:
        stock_sql_str = "select t.symbol ,t.Open,t.High ,t.Low ,t.Close,t.Volume ,t.amount,t.date  from stock_data t where t.date between '%s' and '%s' order by t.date" % (
            start_dt, end_dt)
    with sqlite3.connect(database=database_path) as con:
        # OHLCV
        # stock_sql_str = "select t.symbol ,t.Open,t.High ,t.Low ,t.Close,t.Volume ,t.amount,t.date  from stock_data t where t.date between '%s' and '%s' order by t.date" % (
        #     start_dt, end_dt)
        data = pd.read_sql_query(
            sql=stock_sql_str,
            con=con,
            index_col='date',
            parse_dates=['date']
        )
    return data


def main():
    # logger.remove()
    # logger.add(sys.stdout,format="",level="DEBUG")
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TrendFollower)

    # strats = cerebro.optstrategy(
    #     TrendFollower,
    #     maperiod=range(10, 31)
    # )
    start_dt = datetime.datetime(2024, 1, 1)
    end_dt = datetime.datetime(2024, 1, 5)  # 获取50天的数据，确保有足够数据计算移动平均线

    hkex_cal = query_data(symbol='HKEXCAL', start_dt=start_dt.strftime("%Y-%m-%d"), end_dt=end_dt.strftime("%Y-%m-%d"))
    hkex_cal_data_feed = btfeeds.PandasData(
        dataname=hkex_cal,
        fromdate=start_dt,
        todate=end_dt,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=None
    )

    cerebro.adddata(hkex_cal_data_feed)

    cerebro.broker.setcash(1000000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    longbridge_comminfo = LBCommInfo(commission=0.005)
    cerebro.broker.addcommissioninfo(longbridge_comminfo)

    cerebro.run()
    # cerebro.plot()


if __name__ == "__main__":
    main()
