from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import base64
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
from io import BytesIO

import backtrader as bt
import pandas as pd
import pymysql
from sqlalchemy import create_engine

from myStrategies.triplesystem import TripleSystem
# Bokeh
# from backtrader_plotting import Bokeh
# from backtrader_plotting.schemes import Tradimo


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TripleSystem)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # day_data_path = os.path.join(modpath,'data\\300256SZ_day.csv')
    # week_data_path = os.path.join(modpath, 'data\\300256SZ_week.csv')
    # month_data_path = os.path.join(modpath, 'data\\300256SZ_month.csv')

    # day_data = bt.feeds.GenericCSVData(
    #     dataname=day_data_path,
    #     fromdate=datetime.datetime(2012,1,1),
    #     todate=datetime.datetime(2023,12,31),
    #     nullvalue=0.0,
    #     dtformat=('%Y%m%d'),
    #     datetime=2,
    #     open=3,
    #     high=4,
    #     low=5,
    #     close=6,
    #     openinterest=-1
    # )
    # week_data = bt.feeds.GenericCSVData(
    #     dataname=week_data_path,
    #     fromdate=datetime.datetime(2012,1,1),
    #     todate=datetime.datetime(2023,12,31),
    #     nullvalue=0.0,
    #     dtformat=('%Y%m%d'),
    #     datetime=2,
    #     open=3,
    #     high=4,
    #     low=5,
    #     close=6,
    #     openinterest=-1
    # )
    # month_data = bt.feeds.GenericCSVData(
    #     dataname=month_data_path,
    #     fromdate=datetime.datetime(2018,1,1),
    #     todate=datetime.datetime(2023,12,31),
    #     nullvalue=0.0,
    #     dtformat=('%Y%m%d'),
    #     datetime=2,
    #     open=3,
    #     high=4,
    #     low=5,
    #     close=6,
    #     openinterest=-1
    # )

    # Add the Data Feed to Cerebro
    # tframes = dict(daily=bt.TimeFrame.Days, weekly=bt.TimeFrame.Weeks,
    #                monthly=bt.TimeFrame.Months)
    # cerebro.adddata(day_data) # data
    # cerebro.adddata(week_data) # data1
    # cerebro.resampledata(day_data, timeframe=bt.TimeFrame.Weeks, compression=1)
    # cerebro.adddata(month_data) # data2
    # cerebro.resampledata(day_data, timeframe=tframes['monthly'], compression=1)

    # data = MySQLDataFeed(
    #     dbhost='localhost',
    #     dbname='tushare',
    #     dbuser='tushare',
    #     dbpass='jdyHKsi#94se',
    #     table='daily',
    #     start_time='2022-01-01',
    #     end_time='2022-01-31',
    #     stock_code='300256.SZ'
    # )
    # Connect to the MySQL database
    host='localhost'
    user='tushare'
    password='jdyHKsi#94se'
    database='tushare'
    port=3306

    url_str = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8'%(user,password,host,port,database)
    print(url_str)
    engine = create_engine(url_str)
    query = '''
        select trade_date,open,high,low,close,vol
        from daily 
        where ts_code = "300256.SZ" 
          and trade_date between "20210101" and "20221231"
    '''
    df = pd.read_sql_query(query,
                           engine,
                           parse_dates=['trade_date']
                           )

    data = bt.feeds.PandasData(
        # dtformat=('%Y%m%d'),
        dataname=df,
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
    )
    cerebro.adddata(data)

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
    fig = cerebro.plot()
    # fig[0][0].savefig('./test.png', format="png")

    # fig = cerebro.plot()[0][0]

    # fig.savefig('./test.png', format="png")
