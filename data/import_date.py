import sqlite3
import pandas as pd
import os
from pathlib import Path
import argparse

def import_stock_data(stock_ids):
    # 连接数据库
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    # 创建表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_data (
        stock_id TEXT,
        company_name TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        amount REAL,
        turnover_rate REAL,
        change_amount REAL,
        change_percent REAL,
        pe_ratio REAL,
        ps_ratio REAL,
        pcf_ratio REAL,
        market_cap REAL,
        prev_close REAL,
        change REAL
    )
    ''')

    # 定义列名映射
    column_mapping = {
        '公司名称': 'company_name',
        '日期': 'date',
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '成交量(股)': 'volume',
        '成交额(元)': 'amount',
        '换手率(%)': 'turnover_rate',
        '涨跌额': 'change_amount',
        '涨跌幅(%)': 'change_percent',
        '市盈率(PE)': 'pe_ratio',
        '市销率(PS)': 'ps_ratio',
        '市现率(PCF)': 'pcf_ratio',
        '总市值': 'market_cap',
        '前收盘价': 'prev_close',
        '涨跌额': 'change'
    }

    # 获取所有CSV文件
    csv_dir = Path('data/hk')
    csv_files = list(csv_dir.glob('*.csv'))

    # 如果stock_ids包含-1，则导入所有文件
    if '-1' in stock_ids:
        stock_ids = [f.stem for f in csv_files]

    # 导入每个文件
    for csv_file in csv_files:
        # 获取股票代码（文件名）
        stock_id = csv_file.stem
        
        # 如果指定了特定的股票代码，则只导入这些股票的数据
        if stock_id not in stock_ids:
            continue
            
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file, encoding='gbk')
            
            # 重命名列
            df = df.rename(columns=column_mapping)
            
            # 添加stock_id列
            df['stock_id'] = stock_id
            
            # 将数据写入数据库
            df.to_sql('stock_data', conn, if_exists='append', index=False)
            
            print(f'已导入 {stock_id} 的数据')
        except Exception as e:
            print(f'导入 {stock_id} 时出错: {str(e)}')

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

    print('数据导入完成！')

if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='导入股票数据到SQLite数据库')
    parser.add_argument('stock_ids', nargs='+', help='要导入的股票代码列表，使用-1导入所有股票')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 执行导入
    import_stock_data(args.stock_ids)