import pymysql
from .interface import DefaultInterface

pymysql.install_as_MySQLdb()

class MYSQL(DefaultInterface):
    def connect(self):
        try:
            self._con = pymysql.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                port=self._port,
                db=self._schema,
                charset='utf8')
        except Exception as e:
            raise Exception(f'mysql connect Fail !! error msg: {e}')
        
    def close(self):
        if self._con is not None:
            self._con.close()
            self._con = None