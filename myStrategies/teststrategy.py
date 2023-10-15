import backtrader as bt
from myIndictors import *
from myStrategies import StrategyLogger


class TestStrategy(StrategyLogger):
    def __init__(self):
        self.order = None
        self.day_force_index = ForceIndex(self.data)
        # self.week_power_signal = ForceIndex(self.data1)
        self.week_power_signal = PowerSignal(self.data1)
        # self.macd = bt.indicators.MACDHisto()

    def next(self):

        if self.order:
            return

        if self.position and self.day_force_index[0] > 0:
            self.order = self.sell()

        elif self.day_force_index[0] < 0:
            self.order = self.buy()
