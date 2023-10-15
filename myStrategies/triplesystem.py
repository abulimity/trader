import backtrader as bt
import pandas as pd

from myIndictors.powersignal import PowerSignal
from myIndictors.avgdown import AvgDown
from myIndictors.forceindex import ForceIndex
from .custom_strategy import StrategyLogger

import sshtunnel
import pymysql
from sqlalchemy import create_engine
import paramiko
from datetime import datetime


class TripleSystem(StrategyLogger):
    params = {
        'printlog': True,
        'stoptype': bt.Order.StopTrail,
        'trailamount': 0.0,
        'trailpercent': 0.05,
        'fastperiod': 45,
        'slowperiod': 88,
        'signalperiod': 30,
        'emaperiod': 45,
    }

    def __init__(self):
        super().__init__()
        self.buy_signal = 0
        self.order = None
        self.enough_price = -1
        self.order_dict = dict()

        # self.day_power_signal = PowerSignal(self.data)
        self.day_force_index = ForceIndex(self.data)
        self.day_avgDown = AvgDown(self.data)
        self.day_power_signal = PowerSignal(self.data,
                                            fastperiod=self.p.fastperiod,
                                            slowperiod=self.p.slowperiod,
                                            signalperiod=self.p.signalperiod,
                                            emaperiod=self.p.emaperiod)
        self.week_power_signal = PowerSignal(self.data1,
                                             fastperiod=self.p.fastperiod,
                                             slowperiod=self.p.slowperiod,
                                             signalperiod=self.p.signalperiod,
                                             emaperiod=self.p.emaperiod)
        self.day_macd = bt.indicators.MACDHisto(self.data,
                                                period_me1=self.p.fastperiod,
                                                period_me2=self.p.slowperiod,
                                                period_signal=self.p.signalperiod)
        self.week_bollband = bt.indicators.BollingerBands(self.data1, period=self.p.emaperiod, movav=bt.indicators.EMA)

    def next(self):
        '''

        :return:
        '''
        # self.log('Close, %.2f' % self.data.close[0])

        if self.order:
            return

        if not self.position:
            # self.order = self.buy()
            # 如果没有持仓
            if self.week_power_signal[0] == 2 and self.day_force_index[0] < 0:
                # self.log('BUY SIGNNEL,week_power_sign:%.2f, day_force:%.2f' %
                #          (self.week_power_signal[0], self.day_force_index[0]))
                self.order = self.buy(price=self.day_avgDown[0], exectype=bt.Order.Limit, valid=None)
                # self.order = self.buy(price=self.day_avgDown[0], )
                # self.log('BUY SEND,in price:%.2f, enough price:%.2f' %
                #          (self.day_avgDown[0], self.enough_price))
        else:
            #     # 止盈
            #     # 周线 近N次最高值
            #     self.enough_price = self.week_three_highest[0]
            #     self.order = self.sell(price=self.enough_price, exectype=bt.Order.Limit)
            #     self.log('ENOUGH SELL SEND,in price:%.2f, enough price:%.2f' %
            #              (self.day_avgDown[0], self.enough_price))
            # 如果power signal 出现相反信号立即卖出
            if self.day_power_signal[0] < self.day_power_signal[-1]:
                self.order = self.sell(exectype=bt.Order.Market)

        # if self.position and self.order is None:
        #     self.order = self.sell(exectype=self.p.stoptype,
        #                            trailamount=self.p.trailamount,
        #                            trailpercent=self.p.trailpercent)
        #     if self.p.trailamount:
        #         tcheck = self.data.close - self.p.trailamount
        #     else:
        #         tcheck = self.data.close * (1.0 - self.p.trailpercent)
        #     print(','.join(
        #             map(str, [self.datetime.date(), self.data.close[0],
        #                       self.order.created.price, tcheck])
        #         )
        #     )
        #     print('-' * 10)
        # else:
        #     if self.p.trailamount:
        #         tcheck = self.data.close - self.p.trailamount
        #     else:
        #         tcheck = self.data.close * (1.0 - self.p.trailpercent)
        #     print(','.join(
        #         map(str, [self.datetime.date(), self.data.close[0],
        #                   self.order.created.price, tcheck])
        #         )
        #     )

        #     # 止损
