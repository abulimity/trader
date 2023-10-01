from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# import base64
# import datetime  # For datetime objects
# import os.path  # To manage paths
# import sys  # To find out the script name (in argv[0])
# from io import BytesIO

import backtrader as bt
import pandas as pd
import pymysql
from sqlalchemy import create_engine

from backtrader_plotly.plotter import BacktraderPlotly
from backtrader_plotly.scheme import PlotScheme
import plotly.io

from myStrategies.test_strategy import TestStrategy
# Bokeh
# from backtrader_plotting import Bokeh
# from backtrader_plotting.schemes import Tradimo


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy)

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
          and trade_date between "20210101" and "20210228"
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
    # define plot scheme with new additional scheme arguments
    scheme = PlotScheme(decimal_places=5, max_legend_text_width=16)

    figs = cerebro.plot(BacktraderPlotly(show=False, scheme=scheme))
    # figs[0][0].savefig('/home/abulimity/project/webapp/static/test.png')
    # buffer = BytesIO()
    # figs[0][0].savefig(buffer)
    # plot_data = buffer.getvalue()
    # # 将matplotlib图片转换为HTML
    # imb = base64.b64encode(plot_data)  # 对plot_data进行编码
    # ims = imb.decode()
    # imd = "data:image/png;base64," + ims

    # directly manipulate object using methods provided by `plotly`
    for i, each_run in enumerate(figs):
        for j, each_strategy_fig in enumerate(each_run):
            # open plot in browser
            each_strategy_fig.show()

            # save the html of the plot to a variable
            html = plotly.io.to_html(each_strategy_fig, full_html=False)

            # write html to disk
            plotly.io.write_html(each_strategy_fig, f'{i}_{j}.html', full_html=True)