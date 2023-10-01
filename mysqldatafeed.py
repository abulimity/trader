
import backtrader as bt
import pymysql
from sqlalchemy import create_engine
import pandas as pd

class MySQLDataFeed(bt.feeds.PandasDirectData):
    params = (
        ('dbhost', 'localhost'),
        ('dbname', 'mydatabase'),
        ('dbuser', 'myuser'),
        ('dbpass', 'mypassword'),
        ('table', 'mytable'),
        ('dtformat', '%Y-%m-%d %H:%M:%S'),
        ('start_time', None),
        ('end_time', None),
        ('stock_code', None),
    )

    def __init__(self):
        super().__init__()

        self.db = None
        self.cursor = None

    def start(self):
        self.db = pymysql.connect(
            host=self.params.dbhost,
            user=self.params.dbuser,
            password=self.params.dbpass,
            database=self.params.dbname
        )
        self.cursor = self.db.cursor()

        super().start()

    def stop(self):
        super().stop()

        self.cursor.close()
        self.db.close()

    def _load(self):
        query = f"SELECT * FROM {self.params.table} WHERE stock_code = '{self.params.stock_code}'"
        if self.params.start_time:
            query += f" AND datetime >= '{self.params.start_time}'"
        if self.params.end_time:
            query += f" AND datetime <= '{self.params.end_time}'"

        self.cursor.execute(query)
        data = self.cursor.fetchall()

        # Convert data to pandas DataFrame
        df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], format=self.params.dtformat)
        df.set_index('datetime', inplace=True)

        return df