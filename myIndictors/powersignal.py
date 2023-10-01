import backtrader as bt

class PowerSignal(bt.Indicator):
    lines = (
            'powerSign',
            'macd',
             # 'isUpOfMacd',
             # 'isUpOfEMA',
             )
    params = (
        ('fastperiod', 12),
        ('slowperiod', 26),
        ('signalperiod', 9),
        # ('macdhist', bt.indicators.MACDHisto),
        ('emaperiod', 30),
        # ('emab', bt.indicators.MovAv.EMA)
    )

    def __init__(self):
        super(PowerSignal, self).__init__()
        self.addminperiod(self.p.emaperiod)

        self.lines.macd= _macdhist = bt.indicators.MACDHisto(period_me1=self.p.fastperiod,
                                period_me2=self.p.slowperiod,
                                period_signal=self.p.signalperiod).histo
        self.lines.isUpOfMacd = bt.Cmp(_macdhist, _macdhist(-1))
        # self.lines.isUpOfMacd = IsUpOfMacd(self.data,
        #                                    period_me1=self.p.fastperiod,
        #                                    period_me2=self.p.slowperiod,
        #                                    period_signal=self.p.signalperiod)
        _ema = bt.indicators.EMA(period=self.p.emaperiod)
        # self.lines.isUpOfEMA = IsUpOfEMA(self.data, period=self.p.emaperiod)
        self.lines.isUpOfEMA = bt.Cmp(_ema, _ema(-1))
        self.lines.powerSign = self.lines.isUpOfMacd + self.lines.isUpOfEMA