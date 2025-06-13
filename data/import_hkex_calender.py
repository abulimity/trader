import pandas_market_calendars as mcal
import sqlite3
from datetime import datetime, timedelta
from setting import database_path

# Get HKEX calendar
hkex = mcal.get_calendar('HKEX')

# Get trading dates for the last 5 years
end_date = datetime(2025, 5, 30)
start_date = datetime(1995, 1, 1)
trading_dates = hkex.valid_days(start_date=start_date, end_date=end_date)

# Connect to SQLite database
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Insert trading dates into stock_data table
for date in trading_dates:
    cursor.execute('''
        INSERT INTO stock_data (symbol, date,Open,High,Low,Close,Volume,amount)
        VALUES (?, ?,?,?,?,?,?,?)
    ''', ('HKEXCAL', date.strftime('%Y-%m-%d'), 0, 0, 0, 0, 0, 0))

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Successfully inserted {len(trading_dates)} trading dates for HKEX calendar")

# table_name:stock_data
