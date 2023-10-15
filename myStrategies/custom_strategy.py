import sys

from backtrader import Strategy
from loguru import logger
from functools import partialmethod


class StrategyLogger(Strategy):
    params = dict(
        printlog=True,
        log_enable_list=[
            "FUND",
            "ORDER",
            "TRADE"
        ],
        color={
            "CASHVALUE": "cyan",
            "FUND": "cyan",
            "ORDER": "green",
            "TRADE": "red"
        },
        stdout=True,
        db=False
    )

    def __init__(self):
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self._init_log()

    def _init_log(self):

        logger.remove()
        # max_leve_length = max(len(x) for x in self.p.log_enable_list)
        format_str = "{time:HH:mm:ss.SS} | <level>{level:^5}</level> | {message}"
        logger.add(sys.stdout, format=format_str)

        logger.level("CASHVALUE", no=11, color="<cyan>")
        logger.level("FUND", no=12, color="<cyan>")
        logger.level("ORDER", no=13, color="<green>")
        logger.level("TRADE", no=14, color="<red>")
        logger.level("NEXT", no=14, color="<red>")

    def next(self):
        # add daily split line
        _log_name = "NEXT"
        trade_date = self.datas[0].datetime.date(0)
        msg = "--------------------{}--------------------".format(trade_date)
        logger.log(_log_name, msg)

        # check indicators status

    def notify_cashvalue(self, cash, value):
        _log_name = "CASHVALUE"
        if _log_name not in self.p.log_enable_list:
            return
        trade_date = self.datas[0].datetime.date(0)
        msg = "{} | {}".format(trade_date, cash)
        logger.log(_log_name, msg)

    def notify_fund(self, cash, value, fundvalue, shares):
        _log_name = "FUND"
        if _log_name not in self.p.log_enable_list:
            return
        trade_date = self.datas[0].datetime.date(0)
        # add daily split line
        # msg = "--------------------{}--------------------".format(trade_date)
        # logger.log(_log_name, msg)

        msg = "{} | 账户现金：{:.2f},账户总市值：{:.2f},持仓金额：{:.2f}, 持仓份额：{:.2f}".format(
            trade_date,
            cash,
            value,
            fundvalue,
            shares
        )
        logger.log(_log_name, msg)

    def notify_order(self, order):
        _log_name = "ORDER"
        if _log_name not in self.p.log_enable_list:
            return
        trade_date = self.datas[0].datetime.date(0)
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                msg = "{} | 买入订单-已执行,订单号：{},标的：{},成交价格: {:.2f},成交量：{},成交金额: {:.2f},手续费：{:.2f}".format(
                    trade_date,
                    order.ref,
                    order.data._name,
                    order.executed.price,
                    order.executed.size,
                    order.executed.value,
                    order.executed.comm
                )
                logger.log("ORDER", msg)

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                msg = "{} | 卖出订单-已执行,订单号：{},标的：{},成交价格: {:.2f},成交量：{},成交金额: {:.2f},手续费：{:.2f}".format(
                    trade_date,
                    order.ref,
                    order.data._name,
                    order.executed.price,
                    order.executed.size,
                    order.executed.value,
                    order.executed.comm
                )
                logger.log(_log_name, msg)

            # self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            msg = "订单被取消/追加保证金/拒绝。Order Canceled/Margin/Rejected"
            logger.log(_log_name, msg)

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        _log_name = "TRADE"
        if _log_name not in self.p.log_enable_list:
            return
        if not trade.isclosed:
            return
        msg = "OPERATION PROFIT, GROSS %.2f, NET %.2f".format(
            trade.pnl, trade.pnlcomm)
        logger.log(_log_name, msg)
    # TODO: 暂时没有使用
    # def notify_store(self, msg, *args, **kwargs):
    #     pass
    #
    # def notify_timer(self, timer, when, *args, **kwargs):
    #     pass
    #
    # def notify_data(self, data, status, *args, **kwargs):
    #     pass
