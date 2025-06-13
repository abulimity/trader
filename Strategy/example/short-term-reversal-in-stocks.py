# region imports
from AlgorithmImports import *

# endregion
# https://quantpedia.com/strategies/short-term-reversal-in-stocks/
#
# 投资组合由市值最大的100家公司组成。
# 投资者做多上周表现最差的10只股票，
# 做空上月表现最好的10只股票。每周进行一次再平衡。
#
# QC实现的变化：
#   - 由于全市场筛选计算量大，首先选取流动性最好的500只股票作为初筛。
#   - 再从中选取市值最大的100只股票进行动量排序。


class ShortTermReversalEffectinStocks(QCAlgorithm):
    def Initialize(self):
        # 设置回测起始日期
        self.SetStartDate(2000, 1, 1)
        # 设置初始资金
        self.SetCash(100000)

        # 添加标的SPY（仅用于调度）
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol

        # 粗筛股票数量（流动性前500）
        self.coarse_count = 500
        # 每组股票数量（做多/做空各10只）
        self.stock_selection = 10
        # 精筛后市值最大的股票数量
        self.top_by_market_cap_count = 100

        # 价格窗口长度（21天，约一个月）
        self.period = 21

        self.long = []   # 做多股票列表
        self.short = []  # 做空股票列表

        # 存储股票历史收盘价数据
        self.data = {}

        self.day = 1  # 用于每周调仓的计数器
        self.selection_flag = False  # 是否进行选股标志
        self.UniverseSettings.Resolution = Resolution.Daily
        # 添加股票池筛选函数
        self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)
        # 每天开盘后调度Selection函数
        self.Schedule.On(
            self.DateRules.EveryDay(self.symbol),
            self.TimeRules.AfterMarketOpen(self.symbol),
            self.Selection,
        )

    def OnSecuritiesChanged(self, changes):
        # 新增股票时，设置手续费模型和杠杆
        for security in changes.AddedSecurities:
            security.SetFeeModel(CustomFeeModel())
            security.SetLeverage(5)

    def CoarseSelectionFunction(self, coarse):
        # 每天更新股票的收盘价滚动窗口
        for stock in coarse:
            symbol = stock.Symbol

            # 更新月度价格数据
            if symbol in self.data:
                self.data[symbol].update(stock.AdjustedPrice)

        # 不是调仓日则股票池不变
        if not self.selection_flag:
            return Universe.Unchanged

        # 选取有基本面数据、美国市场、价格大于1美元的流动性前500只股票
        selected = sorted(
            [
                x
                for x in coarse
                if x.HasFundamentalData and x.Market == "usa" and x.Price > 1
            ],
            key=lambda x: x.DollarVolume,
            reverse=True,
        )
        selected = [x.Symbol for x in selected][: self.coarse_count]

        # 对新股票初始化价格滚动窗口，并用历史数据填充
        for symbol in selected:
            if symbol in self.data:
                continue

            self.data[symbol] = SymbolData(self.period)
            history = self.History(symbol, self.period, Resolution.Daily)
            if history.empty:
                self.Log(f"Not enough data for {symbol} yet")
                continue
            closes = history.loc[symbol].close
            for time, close in closes.iteritems():
                self.data[symbol].update(close)

        # 只返回已准备好（有足够历史数据）的股票
        return [x for x in selected if self.data[x].is_ready()]

    def FineSelectionFunction(self, fine):
        # 剔除市值为0的股票
        fine = [x for x in fine if x.MarketCap != 0]

        # 按市值降序排列，选取前100只股票
        sorted_by_market_cap = sorted(fine, key=lambda x: x.MarketCap, reverse=True)
        top_by_market_cap = [
            x.Symbol for x in sorted_by_market_cap[: self.top_by_market_cap_count]
        ]

        # 计算每只股票的月度和周度收益率
        month_performances = {
            symbol: self.data[symbol].monthly_return() for symbol in top_by_market_cap
        }
        week_performances = {
            symbol: self.data[symbol].weekly_return() for symbol in top_by_market_cap
        }

        # 按月度收益率降序排列（表现最好在前）
        sorted_by_month_perf = [
            x[0]
            for x in sorted(
                month_performances.items(), key=lambda item: item[1], reverse=True
            )
        ]
        # 按周度收益率升序排列（表现最差在前）
        sorted_by_week_perf = [
            x[0] for x in sorted(week_performances.items(), key=lambda item: item[1])
        ]

        # 选取周度表现最差的10只股票做多
        self.long = sorted_by_week_perf[: self.stock_selection]

        # 选取月度表现最好的10只股票做空（不与做多股票重复）
        for symbol in sorted_by_month_perf:  # Month performances are sorted descending
            if symbol not in self.long:
                self.short.append(symbol)

            if len(self.short) == 10:
                break

        # 返回做多和做空股票列表
        return self.long + self.short

    def OnData(self, data):
        # 不是调仓日则直接返回
        if not self.selection_flag:
            return
        self.selection_flag = False

        # 卖出所有不在最新股票池中的持仓
        invested = [x.Key for x in self.Portfolio if x.Value.Invested]
        for symbol in invested:
            if symbol not in self.long + self.short:
                self.Liquidate(symbol)

        # 分别买入做多股票、卖空做空股票，等权分配资金
        # 杠杆组合：100%做多，100%做空
        for symbol in self.long:
            if (
                self.Securities[symbol].Price != 0
                and self.Securities[symbol].IsTradable
            ):
                self.SetHoldings(symbol, 1 / len(self.long))

        for symbol in self.short:
            if (
                self.Securities[symbol].Price != 0
                and self.Securities[symbol].IsTradable
            ):
                self.SetHoldings(symbol, -1 / len(self.short))

        # 清空做多、做空列表，等待下次调仓
        self.long.clear()
        self.short.clear()

    def Selection(self):
        # 每5天（每周）进行一次调仓
        if self.day == 5:
            self.selection_flag = True

        self.day += 1
        if self.day > 5:
            self.day = 1


class SymbolData:
    def __init__(self, period):
        # 用RollingWindow存储历史收盘价
        self.closes = RollingWindow[float](period)
        self.period = period

    def update(self, close):
        # 添加新收盘价
        self.closes.Add(close)

    def is_ready(self) -> bool:
        # 判断是否有足够历史数据
        return self.closes.IsReady

    def weekly_return(self) -> float:
        # 计算最近一周收益率
        return self.closes[0] / self.closes[5] - 1

    def monthly_return(self) -> float:
        # 计算最近一个月收益率
        return self.closes[0] / self.closes[self.period - 1] - 1


# 自定义手续费模型
class CustomFeeModel(FeeModel):
    def GetOrderFee(self, parameters):
        # 手续费=价格*数量*万分之0.5
        fee = parameters.Security.Price * parameters.Order.AbsoluteQuantity * 0.00005
        return OrderFee(CashAmount(fee, "USD"))