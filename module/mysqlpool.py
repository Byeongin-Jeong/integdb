import pymysql
from pymysqlpool import ConnectionPool
from .interface import DefaultInterface

pymysql.install_as_MySQLdb()

class MySQLPool(DefaultInterface):
    def connect(self):
        try:
            # DB Pool
            self.config = {
                "host": self._host,
                "user": self._user,
                "port": self._port,
                "password": self._password,
                "database": self._schema
            }
            self.pool = ConnectionPool(**self.config)
        except Exception as e:
            raise Exception(f'mysql Pool connect Fail !! error msg: {e}')