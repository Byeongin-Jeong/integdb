import pymssql
from .interface import DefaultInterface

class MSSQL(DefaultInterface):
    def connect(self):
        try:
            self._con = pymssql.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                port=self._port,
                database=self._schema,
                charset='utf8')
        except Exception as e:
            raise Exception(f'mssql connect Fail !! error msg: {e}')
        
    def close(self):
        if self._con is not None:
            self._con.close()
            self._con = None