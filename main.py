from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
from sqlalchemy import create_engine

from myStrategies.triplesystem import TripleSystem
# Bokeh
# from backtrader_plotting import Bokeh
# from backtrader_plotting.schemes import Tradimo
import sshtunnel
import pymysql
import paramiko
import pandas as pd
from datetime import datetime

from backtrader_plotly.plotter import BacktraderPlotly
from myplotter import MyPlottly
from backtrader_plotly.scheme import PlotScheme
import plotly.io

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


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TripleSystem)

    day_query_str = '''
        select trade_date,open,high,low,close,vol
        from daily 
        where ts_code = "300256.SZ" 
          and trade_date between "20170101" and "20231231"
    '''
    week_query_str = '''
        select trade_date,open,high,low,close,vol
        from weekly
        where ts_code = "300256.SZ"
          and trade_date between "20170101" and "20231231";
    '''
    day_df = query(day_query_str)
    week_df = query(week_query_str)

    day_data = bt.feeds.PandasData(
        # dtformat=('%Y%m%d'),
        dataname=day_df,
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
    )
    week_data = bt.feeds.PandasData(
        # dtformat=('%Y%m%d'),
        dataname=week_df,
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
        timeframe=bt.TimeFrame.Weeks
    )

    cerebro.adddata(day_data)
    cerebro.adddata(week_data)
    # cerebro.replaydata(day_data, timeframe=bt.TimeFrame.Weeks)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # Set the commission
    cerebro.broker.setcommission(commission=0.003)

    # Run over everything
    cerebro.run()
    # b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    # cerebro.plot(b)
    figs = cerebro.plot(style='bar')

    # # define plot scheme with new additional scheme arguments
    # scheme = PlotScheme(decimal_places=5, max_legend_text_width=16)
    #
    # figs = cerebro.plot(MyPlottly(show=False, scheme=scheme))
    #
    # # directly manipulate object using methods provided by `plotly`
    # for i, each_run in enumerate(figs):
    #     for j, each_strategy_fig in enumerate(each_run):
    #         # open plot in browser
    #         each_strategy_fig.show()
    #
    #         # save the html of the plot to a variable
    #         html = plotly.io.to_html(each_strategy_fig, full_html=False)
    #
    #         # write html to disk
    #         plotly.io.write_html(each_strategy_fig, f'{i}_{j}.html', full_html=True)

