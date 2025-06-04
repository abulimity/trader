from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
from pathlib import Path
from loguru import logger

import backtrader as bt
import backtrader.feeds as btfeeds
import datetime


class LBCommInfo(bt.CommInfoBase):
    params = (
        # ('commission', 1.0),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
        ('percabs', False)
    )

    def _getcommission(self, size, price, pseudoexec):
        platform_fee = 15

        order_amount = size * price
        # 交收费 0.002% * 成交金额，最低 2 港元，最高 100 港元
        _fee_1 = 0.002 / 100 * order_amount
        if _fee_1 < 2:
            fee_1 = 2
        elif _fee_1 >= 2 and _fee_1 < 100:
            fee_1 = _fee_1
        elif _fee_1 >= 100:
            fee_1 = 100
        else:
            fee_1 = _fee_1
        # 印花税 0.1% * 成交金额，不足 1 港元作 1 港元计
        _fee_2 = 0.1 / 100 * order_amount
        if _fee_2 < 1:
            fee_2 = 1
        else:
            fee_2 = _fee_2
        # 交易费 0.00565% * 成交金额，最低 0.01 港元
        _fee_3 = 0.00565 / 100 * order_amount
        if _fee_3 < 0.01:
            fee_3 = 0.001
        else:
            fee_3 = _fee_3

        # 交易征费 0.0027% * 成交金额，最低 0.01 港元
        _fee_4 = 0.0027 / 100 * order_amount
        if _fee_4 < 0.01:
            fee_4 = 0.001
        else:
            fee_4 = _fee_4
        # 财务汇报 0.00015% * 成交金额，最低 0.01 港元
        _fee_5 = 0.00015 / 100 * order_amount
        if _fee_5 < 0.01:
            fee_5 = 0.001
        else:
            fee_5 = _fee_4
        comm_value = round(platform_fee + fee_1 + fee_2 + fee_3 + fee_4 + fee_5, 2)
        return comm_value


class TestStrategy(bt.Strategy):
    params = (
        ('exitbars', 5),
        ('maperiod', 10)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.maperiod)
        bt.indicators.ATR(self.datas[0], plot=True)

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

    def next(self):
        # logger.info("trade_date:%s,Close:%.2f" % (self.datas[0].datetime.date(0), self.dataclose[0]))

        if self.order:
            return

        if not self.position:

            if self.dataclose[0] > self.sma[0]:
                logger.info("trade_date:%s,BUY CREATE:%.2f" % (self.datas[0].datetime.date(0), self.dataclose[0]))
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                logger.info("trade_date:%s,SELL CREATE:%.2f" % (self.datas[0].datetime.date(0), self.dataclose[0]))
                self.order = self.sell()

    def stop(self):
        logger.info('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)


if __name__ == '__main__':
    # logger.remove()
    # logger.add(sys.stdout,format="",level="DEBUG")
    cerebro = bt.Cerebro()

    strats = cerebro.optstrategy(
        TestStrategy,
        maperiod=range(10,31)
    )
    data_path = Path("data")
    data_file = data_path.joinpath("00001.csv")

    # 公司名称,日期,开盘价,最高价,最低价,收盘价,成交量(股)
    data_feed = btfeeds.GenericCSVData(
        dataname=data_file,
        fromdate=datetime.datetime(2025, 1, 2),
        todate=datetime.datetime(2025, 5, 30),
        nullvalue=float(0.0),
        dtformat="%Y-%m-%d",
        datetime=1,
        open=2,
        high=3,
        low=4,
        close=5,
        volume=6,
        openinterest=-1
    )
    cerebro.adddata(data_feed)

    cerebro.broker.setcash(1000000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    longbridge_comminfo = LBCommInfo(commission=0.005)
    cerebro.broker.addcommissioninfo(longbridge_comminfo)

    cerebro.run()
    # cerebro.plot()