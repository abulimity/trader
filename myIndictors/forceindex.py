import backtrader as bt
class ForceIndex(bt.Indicator):
    lines = ('forceIndex',)
    params = (
        ('emaperiod', 2),
        # ('ema', bt.indicators.MovAv.EMA)
    )
    plotinfo = dict(plot=True,
                    plothlines=[0, ]
                    # plotymargin=0.05,
                    # plotyhlines=[-1.0, 1.0],
                    # subplot=False,
                    # plotname='isUpOfEMA',
                    # plotlinelabels=True
                    )

    plotlines = dict(
        forceIndex=dict(_fill_gt=(0, 'red'), _fill_lt=(0, 'green'))
    )

    # plotlines = dict(
    #     haDelta=dict(color='red'),
    #     smoothed=dict(color='grey', _fill_gt=(0, 'green'), _fill_lt=(0, 'red'))
    # )

    def __init__(self):
        super(ForceIndex, self).__init__()
        _forceIndex = self.data.volume * (self.data.close - self.data.close(-1))
        self.lines.forceIndex = bt.indicators.EMA(_forceIndex, period=self.p.emaperiod)