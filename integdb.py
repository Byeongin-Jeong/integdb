from module.mysql import MYSQL
from module.mssql import MSSQL
from module.mysqlpool import MySQLPool

class Controller():
    def __init__(self, host, user, password, port, schema, mysqlpool=False):
        if mysqlpool is False:
            self.MySQL = MYSQL(host, user, password, port, schema, mysqlpool)
        else:
            self.MySQLPool = MySQLPool(host, user, password, port, schema, mysqlpool)
        self.MsSQL = MSSQL(host, user, password, port, schema, mysqlpool)