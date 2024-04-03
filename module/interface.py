class DefaultInterface():
    def __init__(self, host, user, password, port, schema, mysqlpool):
        self._host = host
        self._user = user
        self._password = password
        self._port = int(port)
        self._schema = schema
        self._con = None
        self._pool = None
        self._ispool = mysqlpool

    def _getcursor(self):
        if self._ispool:
            con = self.pool.get_connection()
            return con, con.cursor()
        else:
            return self._con, self._con.cursor()
        
    def sql_executer_commit(self, sql_context):
        con, cursor = self._getcursor()

        try:
            cursor.execute(sql_context)
            con.commit()
        except Exception as e:
            con.rollback()
            raise Exception(e)
        finally:
            cursor.close()

    def sql_executer_many_commit(self, sql_context, rows):
        con, cursor = self._getcursor()

        try:
            cursor.executemany(sql_context, rows)
            con.commit()
        except Exception as e:
            con.rollback()
            raise Exception(e)
        finally:
            cursor.close()

    def sql_executer(self, sql_context):
        def __dictfetchall(cursor):
            desc = cursor.description 
            return [
                dict(zip([col[0] for col in desc], row)) 
                for row in cursor.fetchall() 
            ]
        con, cursor = self._getcursor()

        try:
            cursor.execute(sql_context)
            rows = __dictfetchall(cursor)
            con.commit()
            return rows
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.close()

    def sql_callproc(self, procname: str, *arg):
        con, cursor = self._getcursor()

        try:
            cursor.callproc(procname, arg)
            con.commit()
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.close()