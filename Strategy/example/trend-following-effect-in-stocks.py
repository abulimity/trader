# https://quantpedia.com/strategies/trend-following-effect-in-stocks/
#
# 趋势跟踪策略：投资组合由美国上市公司组成。通过最低股价和流动性筛选，避免仙股和流动性差的股票。
# 入场信号：当日收盘价大于等于该股历史最高收盘价时买入。
# 退出信号：使用10日平均真实波幅（ATR）作为移动止损。
# 投资者持有所有满足入场条件且未被止损的股票，组合等权分配，每日调仓。
# 每笔交易扣除0.5%手续费（含滑点和佣金）。
#
# QC实现：
#   - 股票池为流动性最好的100只美股。

import numpy as np
from AlgorithmImports import *


class TrendFollowingStocks(QCAlgorithm):

    def Initialize(self):
        # 设置回测起始日期
        self.SetStartDate(2010, 1, 1)
        # 设置初始资金
        self.SetCash(100000)

        # 设置证券初始化器，获取最新价格
        self.SetSecurityInitializer(lambda x: x.SetMarketPrice(self.GetLastKnownPrice(x)))

        self.course_count = 100  # 股票池数量
        self.long = []           # 待买入股票列表

        self.max_close = {}      # 记录每只股票历史最高收盘价
        self.atr = {}            # 记录每只股票的ATR指标

        self.sl_order = {}       # 记录每只股票的止损订单
        self.sl_price = {}       # 记录每只股票的止损价格

        self.selection = []      # 当前股票池
        self.period = 10 * 12 * 21  # 历史数据窗口长度（约10年）

        self.UniverseSettings.Resolution = Resolution.Daily
        # 添加股票池筛选函数
        self.AddUniverse(self.CoarseSelectionFunction)

    def OnSecuritiesChanged(self, changes):
        # 新增股票时，初始化手续费模型、ATR指标和历史最高价
        for security in changes.AddedSecurities:
            security.SetFeeModel(CustomFeeModel())

            symbol = security.Symbol
            if symbol not in self.atr:
                self.atr[symbol] = self.ATR(symbol, 10, Resolution.Daily)

            if symbol not in self.max_close:
                hist = self.History([self.Symbol(symbol)], self.period, Resolution.Daily)
                if 'close' in hist.columns:
                    closes = hist['close']
                    self.max_close[symbol] = max(closes)

    def CoarseSelectionFunction(self, coarse):
        # 股票池筛选：有基本面数据、价格大于5美元，按流动性排序取前100只
        if self.IsWarmingUp:
            return

        selected = sorted([x for x in coarse if x.HasFundamentalData and x.Price > 5],
                          key=lambda x: x.DollarVolume, reverse=True)

        self.selection = [x.Symbol for x in selected[:self.course_count]]

        return self.selection

    def OnData(self, data):
        # 每日调仓主逻辑
        if self.IsWarmingUp:
            return

        # 检查股票是否创新高，满足则加入待买入列表
        for symbol in self.selection:
            if symbol in data.Bars:
                price = data[symbol].Value

                if symbol not in self.max_close: continue

                if price >= self.max_close[symbol]:
                    self.max_close[symbol] = price
                    self.long.append(symbol)

        stocks_invested = [x.Key for x in self.Portfolio if x.Value.Invested]
        count = len(self.long) + len(stocks_invested)
        if count == 0: return

        # 更新已持仓股票的止损单
        for symbol in stocks_invested:
            if not self.Securities[symbol].IsTradable:
                self.Liquidate(symbol)

            if self.atr[symbol].Current.Value == 0: continue

            # 移动止损
            if symbol not in self.sl_price: continue

            self.SetHoldings(symbol, 1 / count)

            new_sl = self.Securities[symbol].Price - self.atr[symbol].Current.Value
            if new_sl > self.sl_price[symbol]:
                update_order_fields = UpdateOrderFields()
                update_order_fields.StopPrice = new_sl  # 更新止损价

                quantity = self.CalculateOrderQuantity(symbol, (1 / count))
                update_order_fields.Quantity = quantity  # 更新止损单数量

                self.sl_price[symbol] = new_sl
                self.sl_order[symbol].Update(update_order_fields)
                # self.Log('SL MOVED on ' + str(symbol) + ' to: ' + str(new_sl))

        # 开新仓：买入创新高且ATR有效的股票，并设置止损单
        for symbol in self.long:
            if not self.Portfolio[symbol].Invested and self.atr[symbol].Current.Value != 0:
                price = data[symbol].Value
                if self.Securities[symbol].IsTradable:
                    unit_size = self.CalculateOrderQuantity(symbol, (1 / count))

                    self.MarketOrder(symbol, unit_size)

                    sl_price = price - self.atr[symbol].Current.Value
                    self.sl_price[symbol] = sl_price
                    if unit_size != 0:
                        self.sl_order[symbol] = self.StopMarketOrder(symbol, -unit_size, sl_price, 'SL')
                    # self.Log('SL SET on ' + str(symbol) + ' to: ' + str(sl_price))

        self.long.clear()


# 自定义手续费模型
class CustomFeeModel(FeeModel):
    def GetOrderFee(self, parameters):
        # 手续费=价格*数量*万分之0.5
        fee = parameters.Security.Price * parameters.Order.AbsoluteQuantity * 0.00005
        return OrderFee(CashAmount(fee, "USD"))