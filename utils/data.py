from datetime import datetime
import paramiko
import sshtunnel
import pandas as pd
import pymysql
from backtrader import TimeFrame
from backtrader.feeds import PandasData


def get_data_from_db(code, start, end, time_frames=["Days",]):
    time_table_dict = {
        "Days": "daily",
        "Weeks": "weekly",
        "Months": "monthly",
    }
    time_frames_dict = {
        "Days": TimeFrame.Days,
        "Weeks": TimeFrame.Weeks,
        "Months": TimeFrame.Months,
    }
    datas = []
    i = 0
    for time_frame in time_frames:
        query_str = '''
            select trade_date,open,high,low,close,vol
            from {table_name} 
            where ts_code = "{code}" 
              and trade_date between "{start_dt}" and "{end_dt}"
        '''.format(table_name=time_table_dict[time_frame], code=code, start_dt=start, end_dt=end)
        print(query_str)
        df = _query_from_db(query_str)
        data = PandasData(
                # dtformat=('%Y%m%d'),
                timeframe=time_frames_dict[time_frame],
                dataname=df,
                name=code+"_"+time_frame,
                datetime=0,
                open=1,
                high=2,
                low=3,
                close=4,
                volume=5,
                openinterest=-1
            )
        datas.append(data)

    return datas


def _query_from_db(q):
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
