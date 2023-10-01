import backtrader as bt
from backtrader.indicators import EMA

class AvgDown(bt.Indicator):
    lines = ('avgDown',)
    params = (
        ('period', 2),
    )

    plotinfo = dict(
        plot=True,
        subplot=False
    )

    def __init__(self):
        super(AvgDown, self).__init__()
        # _ema1 = EMA(self.data(-1), period=self.p.emaperiod)
        _ema = EMA(self.data, period=self.p.period)
        self.lines.avgDown = (_ema - _ema(-1)) + _ema