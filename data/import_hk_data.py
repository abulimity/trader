import os
import pandas as pd
import sqlite3
import sys

def import_hk_data(stock_ids=None):
    # 连接到SQLite数据库
    conn = sqlite3.connect('hk_stocks.db')
    cursor = conn.cursor()
    
    # 创建表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hk_stocks (
        stock_id TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        amount REAL,
        turnover_rate REAL,
        change REAL,
        change_pct REAL,
        pe_ratio REAL,
        ps_ratio REAL,
        pcf_ratio REAL,
        market_cap REAL,
        pre_close REAL,
        change_amt REAL,
        PRIMARY KEY (stock_id, date)
    )
    ''')
    
    # 获取data/hk目录下的所有CSV文件
    data_dir = 'data/hk'
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # 如果指定了stock_ids，只处理这些文件
    if stock_ids and stock_ids != ['-1']:
        csv_files = [f for f in csv_files if f.split('.')[0] in stock_ids]
    
    # 列名映射
    column_mapping = {
        '公司代码': 'stock_id',
        '日期': 'date',
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '成交量(股)': 'volume',
        '成交额(港元)': 'amount',
        '换手率(%)': 'turnover_rate',
        '涨跌额': 'change',
        '涨跌幅(%)': 'change_pct',
        '市盈率(PE)': 'pe_ratio',
        '市销率(PS)': 'ps_ratio',
        '市现率(PCF)': 'pcf_ratio',
        '市值': 'market_cap',
        '前收盘价': 'pre_close',
        '涨跌额': 'change_amt'
    }
    
    for csv_file in csv_files:
        stock_id = csv_file.split('.')[0]
        file_path = os.path.join(data_dir, csv_file)
        
        try:
            # 读取CSV文件，指定编码为GBK
            df = pd.read_csv(file_path, encoding='gbk')
            
            # 重命名列
            df = df.rename(columns=column_mapping)
            
            # 添加stock_id列
            df['stock_id'] = stock_id
            
            # 将数据写入数据库
            df.to_sql('hk_stocks', conn, if_exists='append', index=False)
            
            print(f"成功导入 {stock_id} 的数据")
            
        except Exception as e:
            print(f"导入 {stock_id} 时出错: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    # 从命令行参数获取stock_ids
    stock_ids = sys.argv[1:] if len(sys.argv) > 1 else None
    import_hk_data(stock_ids) 