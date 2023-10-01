import sshtunnel
import MySQLdb
import paramiko

private_key = paramiko.RSAKey.from_private_key('C:/user/abulimity/.ssh/id_rsa')

# 開啟一個通道穿越REMOTE SERVER直到REMOTE PRIVATE SERVER
# 並且將他和local端的port綁定
server = sshtunnel.SSHTunnelForwarder(
        ('8.218.234.114', 22),
        ssh_username="abulimity",
        ssh_pkey=private_key,
        remote_bind_address=('127.0.0.1', 3306)
    )
server.start()
# 使用已和local端綁定的port 去遠端連線MySQL
conn = MySQLdb.connect(host='127.0.0.1',
                  port=server.local_bind_port,
                  user='mysql_user',
                  passwd='mysql_pw',
                  db='db_name')
server.stop()