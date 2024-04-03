class DefaultInterface():
    def __init__(self, host, user, password, port, schema):
        self._host = host
        self._user = user
        self._password = password
        self._port = int(port)
        self._schema = schema
        self._con = None
        
    def sql_executer_commit(self, sql_context):
        cursor = self._con.cursor()

        try:
            cursor.execute(sql_context)
            self._con.commit()
        except Exception as e:
            self._con.rollback()
            raise Exception(e)
        finally:
            cursor.close()

    def sql_executer_many_commit(self, sql_context, rows):
        cursor = self.con.cursor()

        try:
            cursor.executemany(sql_context, rows)
            self._con.commit()
        except Exception as e:
            self._con.rollback()
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
        cursor = self._con.cursor()

        try:
            cursor.execute(sql_context)
            rows = __dictfetchall(cursor)
            self._con.commit()
            return rows
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.close()

    def sql_callproc(self, procname: str, *arg):
        cursor = self._con.cursor()

        try:
            cursor.callproc(procname, arg)
            self._con.commit()
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.close()