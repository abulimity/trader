import backtrader as bt
from myIndictors.powersignal import PowerSignal
from myIndictors.avgdown import AvgDown
from myIndictors.forceindex import ForceIndex


class TripleSystem(bt.Strategy):
    params = {
        'printlog': True,
        'stoptype':  bt.Order.StopTrail,
        'trailamount' : 0.0,
        'trailpercent' : 0.05,
    }

    def __init__(self):
        self.buy_signal = 0
        self.order = None
        self.enough_price = -1

        self.day_power_signal = PowerSignal(self.data)
        self.day_force_index = ForceIndex(self.data)
        self.day_avgDown = AvgDown(self.data)
        self.week_power_signal = PowerSignal(self.data1)
        self.week_force_index = ForceIndex(self.data1)
        self.week_three_highest = bt.indicators.Highest(self.data1,period=40)


    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

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
                self.log('BUY SIGNNEL,week_power_sign:%.2f, day_force:%.2f' %
                         (self.week_power_signal[0], self.day_force_index[0]))
                self.order = self.buy(price=self.day_avgDown[0], exectype=bt.Order.Limit)
                # self.order = self.buy(price=self.day_avgDown[0], )
                self.log('BUY SEND,in price:%.2f, enough price:%.2f' %
                         (self.day_avgDown[0], self.enough_price))
        else:
            # 止盈
            # 周线 近N次最高值
            self.enough_price = self.week_three_highest[0]
            self.order = self.sell(price=self.enough_price, exectype=bt.Order.Limit)
            self.log('ENOUGH SELL SEND,in price:%.2f, enough price:%.2f' %
                     (self.day_avgDown[0], self.enough_price))
        if self.position and self.order is None:
            self.order = self.sell(exectype=self.p.stoptype,
                                   trailamount=self.p.trailamount,
                                   trailpercent=self.p.trailpercent)
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

        #
        #     # 止损


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                # self.buyprice = order.executed.price
                # self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            # self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
