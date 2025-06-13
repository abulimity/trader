import backtrader as bt
class LBCommInfo(bt.CommInfoBase):
    params = (
        # ('commission', 1.0),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC),
        ('percabs', False)
    )

    def _getcommission(self, size, price, pseudoexec):
        platform_fee = 15

        order_amount = size * price
        # 交收费 0.002% * 成交金额，最低 2 港元，最高 100 港元
        _fee_1 = 0.002 / 100 * order_amount
        if _fee_1 < 2:
            fee_1 = 2
        elif _fee_1 >= 2 and _fee_1 < 100:
            fee_1 = _fee_1
        elif _fee_1 >= 100:
            fee_1 = 100
        else:
            fee_1 = _fee_1
        # 印花税 0.1% * 成交金额，不足 1 港元作 1 港元计
        _fee_2 = 0.1 / 100 * order_amount
        if _fee_2 < 1:
            fee_2 = 1
        else:
            fee_2 = _fee_2
        # 交易费 0.00565% * 成交金额，最低 0.01 港元
        _fee_3 = 0.00565 / 100 * order_amount
        if _fee_3 < 0.01:
            fee_3 = 0.001
        else:
            fee_3 = _fee_3

        # 交易征费 0.0027% * 成交金额，最低 0.01 港元
        _fee_4 = 0.0027 / 100 * order_amount
        if _fee_4 < 0.01:
            fee_4 = 0.001
        else:
            fee_4 = _fee_4
        # 财务汇报 0.00015% * 成交金额，最低 0.01 港元
        _fee_5 = 0.00015 / 100 * order_amount
        if _fee_5 < 0.01:
            fee_5 = 0.001
        else:
            fee_5 = _fee_4
        comm_value = round(platform_fee + fee_1 + fee_2 + fee_3 + fee_4 + fee_5, 2)
        return comm_value