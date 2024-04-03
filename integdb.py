from module.mysql import MYSQL
from module.mssql import MSSQL

class Controller():
    def __init__(self, host, user, password, port, schema, mysqlpool=False):
        self.Mysql = MYSQL(host, user, password, port, schema)
        self.Mssql = MSSQL(host, user, password, port, schema)