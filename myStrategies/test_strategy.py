import backtrader as bt

class TestStrategy(bt.Strategy):

    def __int__(self):
        self.sma = bt.indicators.SMA(period=30)

    def next(self):
        if not self.position:
            pass
        else:
            self.order = self.buy()