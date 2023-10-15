import backtrader as bt
from .custom_strategy import StrategyLogger
from myIndictors import *
class Datastrategy(bt.Strategy):

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.buy_signal = 0
        self.order = None
        self.enough_price = -1
        self.order_dict = dict()

        self.day_force_index = ForceIndex(self.data)
        self.day_avgDown = AvgDown(self.data)

        self.day_force_index = ForceIndex(self.data1)
        self.day_avgDown = AvgDown(self.data1)

    def next(self):
        if self.order:
            return
        if not self.position:
            if self.week_power_signal[0] == 2 and self.day_force_index[0] < 0:
                self.order = self.buy(price=self.day_avgDown[0], exectype=bt.Order.Limit, valid=None)
        else:
            if self.day_power_signal[0] < self.day_power_signal[-1]:
                self.order = self.sell(exectype=bt.Order.Market)