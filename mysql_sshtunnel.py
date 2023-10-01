import sshtunnel
import pymysql
import paramiko
import pandas as pd

def query(q):
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
        return pd.read_sql_query(q, conn)