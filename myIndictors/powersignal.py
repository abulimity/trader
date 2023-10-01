import backtrader as bt

class PowerSignal(bt.SignalStrategy):
    params = (
        ('ema_period', 20),
        ('macd_fast_period', 12),
        ('macd_slow_period', 26),
        ('macd_signal_period', 9),
    )

    lines = ('power_signal',)  # Declare the line object

    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(
            self.data, period=self.params.ema_period
        )
        self.macd = bt.indicators.MACDHisto(
            self.data,
            period_me1=self.params.macd_fast_period,
            period_me2=self.params.macd_slow_period,
            period_signal=self.params.macd_signal_period
        )

    def next(self):
        if self.ema[0] > self.ema[-1] and self.macd.macdhist[0] > self.macd.macdhist[-1]:
            self.lines.power_signal[0] = 1
        elif self.ema[0] < self.ema[-1] and self.macd.macdhist[0] < self.macd.macdhist[-1]:
            self.lines.power_signal[0] = -1
        else:
            self.lines.power_signal[0] = 0