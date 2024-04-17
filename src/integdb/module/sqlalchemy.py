import random
import string
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from .interface import SessionConfig

class SQLAlchemy(SessionConfig):
    def __init__(self, host, user, password, port, schema, connection_pool):
        super().__init__(host, user, password, port, schema, connection_pool)

    def _table_column_names(self, table: str) -> str:
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"
        rows = self._engine.execute(query)
        dirty_names = [i[0] for i in rows]
        clean_names = '`' + '`, `'.join(map(str, dirty_names)) + '`'
        return clean_names

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

    def sql_export(self, df: pd.DataFrame, table_name, schema=None):
        try:
            if self._engine is None:
                self._engine = create_engine(url=self._connection_str)

            db_schema = self._schema
            if schema is not None:
                db_schema = schema
            df.to_sql(table_name, con=self._engine, if_exists='append', index=False, schema=db_schema)
        except IntegrityError as e:
            raise IntegrityError(e.statement, e.params, e.orig)
        except Exception as e:
            raise Exception(e)
        
    def sql_export_ignore(self, df: pd.DataFrame, table_name, schema=None):
        temp_table = ''.join(random.choice(string.ascii_letters) for i in range(10))
        is_tmp_table = False
        try:
            if self._engine is None:
                self._engine = create_engine(url=self._connection_str)

            db_schema = self._schema
            if schema is not None:
                db_schema = schema

            df.to_sql(temp_table, con=self._engine, if_exists='append', index=False, schema=db_schema)
            is_tmp_table = True
            columns = self._table_column_names(table=temp_table)
            insert_query = f'INSERT IGNORE INTO {db_schema}.{table_name}({columns}) SELECT {columns} FROM `{temp_table}`'
            self._engine.execute(insert_query)
        except Exception as e:
            raise Exception(e)
        finally:
            # drop temp table
            if is_tmp_table:
                self._engine.execute(f'DROP TABLE IF EXISTS `{temp_table}`')

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