import backtrader as bt
from backtrader.indicator import LinePlotterIndicator
import backtrader.indicators as btind
from myIndictors.powersignal import PowerSignal
from myIndictors.avgdown import AvgDown
from myIndictors.forceindex import ForceIndex


class TripleSystem(bt.Strategy):
    params = {
        'printlog': True,
    }

    def __init__(self):
        self.buy_signal = 0
        self.order = None
        self.enough_price = -1

        self.power_signal = PowerSignal()
        self.force_index = ForceIndex()
        self.enough_price = AvgDown()


    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def prenext(self):
        '''
        在开始执行next()之前，一次性调用n-1次，第n次去调用next
        :return:
        '''
        pass

    def next(self):
        '''

        :return:
        '''
        # self.log('Close, %.2f' % self.data.close[0])

        if self.order:
            return

        if not self.position:
            pass
        else:
            self.order = self.buy()
        # # 如果没有持仓
        #     if self.week_power_sign[0] == 2 and self.day_force[0] < 0:
        #         self.log('BUY SIGNNEL,week_power_sign:%.2f, day_force:%.2f' %
        #                  (self.week_power_sign[0], self.day_force[0]))
        #         self.order = self.buy(price=self.avgDown[0], exectype=bt.Order.Limit)
        #     self.log('BUY SEND,in price:%.2f, enough price:%.2f' %
        #              (self.avgDown[0], self.enough_price))
        #
        # else:
        #     # 止盈
        #     # 周线 近N次最高值
        #     self.enough_price = self.week_three_highest[0]
        #     self.order = self.sell(price=self.enough_price, exectype=bt.Order.Limit)
        #     self.log('SELL SEND,in price:%.2f, enough price:%.2f' %
        #              (self.avgDown[0], self.enough_price))



    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            # if order.isbuy():
            #     self.log(
            #         'BUY Submitted, Price: %.2f, Cost: %.2f, Comm %.2f' %
            #         (order.created.price,
            #          order.created.value,
            #          order.created.comm))
            #
            #     # self.buyprice = order.executed.price
            #     # self.buycomm = order.executed.comm
            # else:  # Sell
            #     self.log('SELL Submitted, Price: %.2f, Cost: %.2f, Comm %.2f' %
            #              (order.created.price,
            #               order.created.value,
            #               order.created.comm))

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
