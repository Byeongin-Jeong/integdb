import random
import string
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from .interface import SessionConfig

class SQLAlchemy(SessionConfig):
    def __init__(self, host, user, password, port, schema, connection_pool):
        super().__init__(host, user, password, port, schema, connection_pool)

    def __table_column_names(self, table: str) -> str:
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"
        rows = self._engine.execute(query)
        dirty_names = [i[0] for i in rows]
        clean_names = '`' + '`, `'.join(map(str, dirty_names)) + '`'
        return clean_names
    
    def __insert_ignore(self, df: pd.DataFrame, db_schema, table_name):
        is_tmp_table = False
        try:
            temp_table = ''.join(random.choice(string.ascii_letters) for _ in range(10))
            # create table and insert temp table
            df.to_sql(temp_table, con=self._engine, if_exists='append', index=False, schema=db_schema)
            is_tmp_table = True
            
            # get temp table column
            columns = self.__table_column_names(table=temp_table)
            
            # insert ignore table
            insert_query = f'INSERT IGNORE INTO {db_schema}.{table_name}({columns}) SELECT {columns} FROM `{temp_table}`'
            self._engine.execute(insert_query)
        except Exception as e:
            raise Exception(e)
        finally:
            # drop temp table
            if is_tmp_table:
                self._engine.execute(f'DROP TABLE IF EXISTS `{temp_table}`')

    def connect(self, db_url="mysql+pymysql"):
        try:
            self._connection_str = f'{db_url}://{self._user}:{self._password}@{self._host}:{self._port}/{self._schema}'
            self._engine = create_engine(url=self._connection_str)
        except Exception as e:
            raise Exception(f'Error connecting to the SQLAlchemy: {e}')
        
    def close(self):
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    # TODO: Schema Check
    # def sql_execute(self, sql_context, return_dict=False):
    #     def __dictfetchall(result):
    #         temp_dict, result_list = {}, []
    #         for rowproxy in result:
    #             # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
    #             for column, value in rowproxy.items():
    #                 temp_dict = {**temp_dict, **{column: value}}
    #             result_list.append(temp_dict)
    #         return result_list
    #     try:
    #         result = self._engine.execute(sql_context)
    #         if return_dict is False:
    #             return result.fetchall()
    #         else:
    #             return __dictfetchall(result)
    #     except Exception as e:
    #         raise Exception(e)

    def sql_export(self, df: pd.DataFrame, table_name, schema=None):
        db_schema = schema if schema is not None else self._schema
        try:
            if self._engine is None:
                self._engine = create_engine(url=self._connection_str)

            df.to_sql(table_name, con=self._engine, if_exists='append', index=False, schema=db_schema)
        except IntegrityError as e:
            error_code = e.orig.args[0]
            error_msg = e.orig.args[1]
            if error_code != 1062:
                raise Exception(error_msg)
            else:
                # Duplicate Key
                self.__insert_ignore(df, db_schema, table_name)
        except Exception as e:
            raise Exception(e)

    def sql_to_pandas(self, sql_context):
        try:
            if self._engine is None:
                self._engine = create_engine(url=self._connection_str)

            df_rows = pd.read_sql(sql_context, con=self._engine)
            return df_rows
        except IntegrityError as e:
            raise IntegrityError(e.statement, e.params, e.orig)
        except Exception as e:
            raise Exception(e)