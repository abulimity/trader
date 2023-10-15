from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
from sqlalchemy import create_engine

from myStrategies import TestStrategy, TripleSystem
# Bokeh
# from backtrader_plotting import Bokeh
# from backtrader_plotting.schemes import Tradimo
import sshtunnel
import pymysql
import paramiko
import pandas as pd
from datetime import datetime
import argparse


def query(q):
    print("start query:%s" % datetime.now())
    private_key = paramiko.RSAKey.from_private_key_file('C:\\Users\\abulimity\\.ssh\\id_rsa')
    with sshtunnel.SSHTunnelForwarder(
            ('8.218.234.114', 22),
            ssh_username="abulimity",
            ssh_pkey=private_key,
            remote_bind_address=('127.0.0.1', 3306)
    ) as server:
        conn = pymysql.connect(host='127.0.0.1',
                               port=server.local_bind_port,
                               user='tushare',
                               passwd='jdyHKsi#94se',
                               db='tushare')
        result = pd.read_sql_query(q, conn, parse_dates=['trade_date'])
        print("end query:%s" % datetime.now())
        return result


def get_data(code, time_frame=bt.TimeFrame.Days):
    time_table_dict = {
        bt.TimeFrame.Days: "daily",
        bt.TimeFrame.Weeks: "weekly",
        bt.TimeFrame.Months: "monthly",
    }
    query_str = '''
        select trade_date,open,high,low,close,vol
        from {table_name} 
        where ts_code = "{code}" 
          and trade_date between "20230101" and "20231231"
    '''.format(table_name=time_table_dict[time_frame], code=code)
    print(query_str)
    df = query(query_str)
    name = code + "_" + time_table_dict[time_frame]
    data = bt.feeds.PandasData(
        # dtformat=('%Y%m%d'),
        timeframe=time_frame,
        dataname=df,
        name=name,
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
    )
    return data


def runstrat():
    args = parse_args()
    tframes = dict(daily=bt.TimeFrame.Days, weekly=bt.TimeFrame.Weeks,
                   monthly=bt.TimeFrame.Months)

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # add strategy
    cerebro.addstrategy(TestStrategy)

    # add data
    if args.timeframe == "daily":
        day_data = get_data(code="300256.SZ", time_frame=tframes[args.timeframe])
        cerebro.adddata(day_data)
    elif args.timeframe == "weekly":
        # add day
        day_data = get_data(code="300256.SZ")
        cerebro.adddata(day_data)
        # add week
        week_data = get_data(code="300256.SZ", time_frame=tframes[args.timeframe])
        cerebro.adddata(week_data)

    # set base config
    set_config(cerebro)

    # Run over everything
    cerebro.run()

    # Plot the result
    cerebro.plot(style='candle')


def set_config(cerebro):
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # Set the commission
    cerebro.broker.setcommission(commission=0.003)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Multitimeframe test')

    parser.add_argument('--timeframe', default='daily', required=False,
                        choices=['daily', 'weekly', 'monhtly'],
                        help='Timeframe to resample to')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()