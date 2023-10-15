import backtrader as bt
from utils import *
from myStrategies import *


def run():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # add strategy
    cerebro.addstrategy(TripleSystem)

    # add data
    datas = get_data_from_db(code="300256.SZ", start="20170101", end="20231001", time_frames=["Days", "Weeks"])
    for d in datas:
        cerebro.adddata(d)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # Set the commission
    cerebro.broker.setcommission(commission=0.003)

    # Run over everything
    cerebro.run()

    # Plot the result
    cerebro.plot(style='candle')

if __name__ == "__main__":
    run()