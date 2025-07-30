from sqlalchemy import create_engine, event, text
from sqlalchemy.engine.url import URL
from sqlalchemy.engine.cursor import LegacyCursorResult

from msal import ConfidentialClientApplication
import urllib
import struct
import subprocess
import pandas as pd
import logging
import random
import json
from numbers import Number

from typing import List

from vava_utils.keyvault import get_secret_from_key_vault

SQL_SERVER = "sql_server"
MYSQL = "mysql"
POSTGRESQL = "postgresql"

LOGGER = logging.getLogger(__name__)


def get_postgresql_helper(
    host, user, port, database=None, password=None, secret=None, key_vault=None, **kwargs
):
    if key_vault and secret:
        password = get_secret_from_key_vault(key_vault, secret)
    if not password:
        raise ValueError("password or secret and valult must be provided for PostgreSQL connection")
    # using old version of psycopg2 (new one is psycopg3) because sql_alchemy < 2 only works with old version
    engine_url = URL.create(
        drivername="postgresql+psycopg2", host=host, username=user, database=database, password=password, port=port
    )
    engine = create_engine(engine_url, pool_pre_ping=True, **kwargs)

    return SQL_Helper(engine, engine_type=POSTGRESQL)


def get_mysql_helper(host, user, port, database=None, password=None, secret=None, key_vault=None, **kwargs):
    if key_vault and secret:
        password = get_secret_from_key_vault(key_vault, secret)
    engine_url = URL.create(
        drivername="mysql+pymysql", host=host, username=user, database=database, password=password, port=port
    )
    engine = create_engine(
        engine_url, connect_args={"ssl": {"ssl_check_hostname": False}}, pool_pre_ping=True, **kwargs
    )
    if not password:
        @event.listens_for(engine, "do_connect")  # https://docs.sqlalchemy.org/en/14/core/engines.html
        def provide_token(dialect, conn_rec, cargs, cparams):
            cmd = "az account get-access-token --resource-type oss-rdbms --output tsv --query accessToken"
            token = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE).stdout.decode("utf-8")
            cparams["password"] = token

    return SQL_Helper(engine, engine_type=MYSQL)


def _get_sqlserver_helper_from_user_password(
    host,
    database,
    user,
    password,
    port,
    db_driver,
    fast_execute_many,
    **kwargs,
):
    conn_str = urllib.parse.quote_plus(
        f"DRIVER={{{db_driver}}};SERVER={host},{port};DATABASE={database};UID={user};PWD={password}"
    )
    engine = create_engine(
        url=URL.create("mssql+pyodbc", query={"odbc_connect": conn_str}),
        fast_executemany=fast_execute_many,
        pool_pre_ping=True,
        **kwargs,
    )
    return SQL_Helper(engine, engine_type=SQL_SERVER)


def _get_sqlserver_helper_from_service_principal(
    host,
    database,
    service_principal_id,
    service_principal_secret,
    tenant_id,
    port,
    db_driver,
    fast_execute_many,
    **kwargs,
):
    creds = ConfidentialClientApplication(
        client_id=service_principal_id,
        client_credential=service_principal_secret,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )

    conn_str = urllib.parse.quote_plus(f"DRIVER={{{db_driver}}};SERVER={host},{port};DATABASE={database}")

    connect_args = {"ansi": False, "TrustServerCertificate": "yes"}
    engine = create_engine(
        url=URL.create("mssql+pyodbc", query={"odbc_connect": conn_str}),
        connect_args=connect_args,
        fast_executemany=fast_execute_many,
        pool_pre_ping=True,
        **kwargs,
    )

    @event.listens_for(engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams):
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        token = creds.acquire_token_for_client(scopes=["https://database.windows.net//.default"])
        token_bytes = token["access_token"].encode("utf-16-le")
        token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
        cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

    return SQL_Helper(engine, engine_type=SQL_SERVER)


def get_sqlserver_helper(
    host,
    database,
    service_principal_id=None,
    service_principal_secret=None,
    tenant_id=None,
    user=None,
    password=None,
    secret=None, 
    key_vault=None,
    port=1433,
    db_driver="ODBC Driver 17 for SQL Server",
    fast_execute_many=True,
    **kwargs,
):
    if key_vault and secret:
        password = get_secret_from_key_vault(key_vault, secret)

    if user and password:
        return _get_sqlserver_helper_from_user_password(
            host,
            database,
            user,
            password,
            port,
            db_driver,
            fast_execute_many,
            **kwargs,
        )
    elif service_principal_id and service_principal_secret and tenant_id:
        return _get_sqlserver_helper_from_service_principal(
            host,
            database,
            service_principal_id,
            service_principal_secret,
            tenant_id,
            port,
            db_driver,
            fast_execute_many,
            **kwargs,
        )
    else:
        raise ValueError(
            "Either user and password or secret and key_vault  or service_principal_id, service_principal_secret and tenant_id must be provided"
        )


def _value_to_str(v):
    if isinstance(v, bool):
        return str(int(v))
    elif isinstance(v, Number):
        return str(v)
    elif isinstance(v, dict) or isinstance(v, list):
        return f"'{json.dumps(v, ensure_ascii=False)}'"
    else:
        return f"'{v}'"


class SQL_Helper:
    def __init__(self, engine, engine_type):
        """
        SQL helper constructor.

        Parameters:
            engine: sqlalchemy.engine.base.Engine instance
        """
        self._engine = engine
        self.engine_type = engine_type

    def from_table(self, table, **kwargs):
        """
        Given a table name, returns a Pandas DataFrame.

        Parameters:
            table (string): table name
            **kwargs: additional keyword parameters passed to pd.read_sql_table

        Returns:
            result (pd.DataFrame): SQL table in pandas dataframe format
        """
        df = pd.read_sql_table(table.lower(), self._engine, **kwargs)
        return df[[c for c in df.columns if c != "my_row_id"]]  # remove my_row_id column (added by MySQL)

    def from_file(self, filename, query_args={}, limit=None, **kwargs):
        """
        Read SQL query from .sql file into a Pandas DataFrame.

        Parameters:
            filename (string): path to file containing the SQL query
            query_args (dict): query string is formatted with those params: string.format(**query_args)
                               example: {'max_date': '2020-01-01'}
            limit (int): maximum number of results
            **kwargs: additional keyword parameters passed to pd.read_sql_query

        Returns:
            result (pd.DataFrame): query results in  Pandas DataFrame format
        """
        if (limit is not None) and (not isinstance(limit, int)):
            raise ValueError("Limit must be of type int")

        with open(filename, "r") as f:
            query_unformated = f.read().rstrip()
        query = query_unformated.format(**query_args)
        query = query if not limit else query.replace(";", f" LIMIT {limit};")
        return self.from_query(query, **kwargs)

    def from_query(self, query, **kwargs):
        """
        Read SQL query into a Pandas DataFrame.

        Parameters:
            query (string): query string
            **kwargs: additional keyword parameters passed to pd.read_sql_query

        Returns:
            result (pd.DataFrame): query results in  Pandas DataFrame format
        """
        return pd.read_sql_query(text(query), self._engine, **kwargs)

    def write_df(
        self, df: pd.DataFrame, table_name: str, chunksize: int = 1000, index: bool = False, if_exists="fail", **kwargs
    ):
        """
        Store Pandas Dataframe into SQL table

        Args:
            df (pd.DataFrame): data to write
            table_name (str): output database table name
            if_exists (str): action to take if table already exists
                * fail,
                * replace
                * append
                * truncate: NEW, truncate table before writing, like 'replace' but keeps structure
            **kwargs: additional keyword parameters passed to df.to_sql
        """
        with self._engine.connect() as conn:
            trans = conn.begin()
            try:
                if if_exists == "truncate":
                    conn.execute(f"TRUNCATE TABLE {table_name}")
                    if_exists = "append"
                df.to_sql(table_name.lower(), conn, chunksize=chunksize, index=index, if_exists=if_exists, **kwargs)
                trans.commit()
            except Exception as ex:
                LOGGER.warning(str(ex))
                trans.rollback()
                raise ex

    def upsert_df(self, df: pd.DataFrame, table_name: str, upsert_cols: List[str], chunksize: int = 1000):
        """
        Store Pandas Dataframe into SQL table with upsert method.

        Args:
            df (pd.DataFrame): data to write
            table_name (str): output database table name
            upsert_cols (List[str]): list columns to use as keys for upserting
            chunksize (int): number of rows in each batch to be written at a time
        """
        if self.engine_type == SQL_SERVER:
            tmp_table_name = f"##{table_name}_tmp_{random.randrange(0, 1000)}"  # This has to be a global table
            create_sql_model = """
                SELECT TOP 0 * INTO dbo.{tmp_table_name} FROM dbo.{table_name}
            """
            set_part_sql_model = "{col} = tmp.{col}"
            update_sql_model = """
                UPDATE {table_name} SET {set_part}
                FROM dbo.{table_name} AS t
                INNER JOIN {tmp_table_name} AS tmp
                ON {upsert_part_cols};
            """
            insert_sql_model = """
                INSERT INTO dbo.{table_name}({comma_col_names})
                SELECT {comma_col_names}
                FROM {tmp_table_name} AS tmp
                WHERE NOT EXISTS
                (
                    SELECT 1 FROM {table_name} 
                    WHERE {not_exists_part_cols}
                );
            """
            col_names = [f"[{x}]" for x in df.columns]
            upsert_cols = [f"[{x}]" for x in upsert_cols]

        elif self.engine_type == MYSQL:
            tmp_table_name = f"{table_name}_tmp_{random.randrange(0, 1000)}"
            create_sql_model = """
                CREATE TEMPORARY TABLE IF NOT EXISTS {tmp_table_name} LIKE {table_name};
            """
            set_part_sql_model = "t.{col} = tmp.{col}"
            update_sql_model = """
                UPDATE {table_name} t
                INNER JOIN {tmp_table_name} tmp ON {upsert_part_cols}
                SET {set_part};
            """
            insert_sql_model = """
                INSERT INTO {table_name}({comma_col_names})
                SELECT {comma_col_names}
                FROM {tmp_table_name} AS tmp
                WHERE NOT EXISTS
                (
                    SELECT 1 FROM {table_name} 
                    WHERE {not_exists_part_cols}
                );
            """
            col_names = [f"`{x}`" for x in df.columns]
            upsert_cols = [f"`{x}`" for x in upsert_cols]

        elif self.engine_type == POSTGRESQL:
            tmp_table_name = f"{table_name}_tmp_{random.randrange(0, 1000)}"
            create_sql_model = f"""
                CREATE TEMP TABLE {tmp_table_name} as TABLE {table_name} WITH NO DATA;
            """
            set_part_sql_model = "t.{col} = tmp.{col}"
            update_sql_model = """
                UPDATE {table_name} t
                SET {set_part}
                INNER JOIN {tmp_table_name} tmp ON {upsert_part_cols};
            """
            insert_sql_model = """
                INSERT INTO {table_name}({comma_col_names})
                SELECT {comma_col_names}
                FROM {tmp_table_name} AS tmp
                WHERE NOT EXISTS
                (
                    SELECT 1 FROM {table_name} 
                    WHERE {not_exists_part_cols}
                );
            """
            col_names = [f"`{x}`" for x in df.columns]
            upsert_cols = [f"`{x}`" for x in upsert_cols]

        else:
            raise NotImplementedError(f"Method not implemented for {self.engine_type} engine")

        try:
            # this is transactional
            with self._engine.connect() as conn:
                trans = conn.begin()
                try:
                    # CREATE tmp table as a copy
                    create_tmp_table_sql = create_sql_model.format(table_name=table_name, tmp_table_name=tmp_table_name)
                    conn.execute(text(create_tmp_table_sql))

                    # First insert in tmp table.
                    df.to_sql(tmp_table_name, conn, if_exists="append", index=False, chunksize=chunksize)

                    # UPDATE Existing
                    set_part = []
                    for col in col_names:
                        set_part.append(set_part_sql_model.format(col=col))
                    set_part = ", ".join(set_part)
                    upsert_part_cols = []
                    for col in upsert_cols:
                        upsert_part_cols.append(f"t.{col} = tmp.{col}")
                    upsert_part_cols = " AND ".join(upsert_part_cols)
                    update_sql = update_sql_model.format(
                        table_name=table_name,
                        tmp_table_name=tmp_table_name,
                        upsert_part_cols=upsert_part_cols,
                        set_part=set_part,
                    )
                    conn.execute(text(update_sql))

                    # INSERT New
                    not_exists_part_cols = []
                    for col in upsert_cols:
                        not_exists_part_cols.append(f"{col} = tmp.{col}")
                    not_exists_part_cols = " AND ".join(not_exists_part_cols)
                    comma_col_names = f'{", ".join(col_names)}'
                    insert_sql = insert_sql_model.format(
                        table_name=table_name,
                        comma_col_names=comma_col_names,
                        tmp_table_name=tmp_table_name,
                        not_exists_part_cols=not_exists_part_cols,
                    )
                    conn.execute(text(insert_sql))

                    # DROP tmp table
                    conn.execute(text(f"DROP TABLE {tmp_table_name};"))

                    trans.commit()
                except Exception as ex:
                    LOGGER.warning(str(ex))
                    trans.rollback()
                    raise ex
        except Exception as ex:
            LOGGER.error(str(ex), exc_info=ex)
            raise ex

    def write_row(self, row, table_name):
        """
        Write single row into SQL table

        Args:
            row (dict): dictionary with keys as column names
            table_name (str): output database table name
        """

        cols = ", ".join([k for k, v in row.items() if not pd.isna(v)])
        values = ", ".join([_value_to_str(v) for k, v in row.items() if not pd.isna(v)])
        insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({values});"

        with self._engine.connect() as conn:
            try:
                conn.execute(insert_query)
            except Exception as ex:
                LOGGER.warning(str(ex))
                raise ex

    def update_row(self, row, keys, table_name):
        """
        Update row from SQL table

        Args:
            row (dict): dictionary with keys as column names
            keys (list): column names to use as keys for updating only matching rows
            table_name (str): output database table name
        """

        update = ", ".join([f"{k} = {_value_to_str(v)}" for k, v in row.items() if not pd.isna(v) and (k not in keys)])
        condition = " AND ".join(
            [f"{k} = {_value_to_str(row[k])}" if not pd.isna(row[k]) else f"{k} IS NULL" for k in keys]
        )
        insert_query = f"UPDATE {table_name} SET {update} WHERE {condition};"

        with self._engine.connect() as conn:
            try:
                conn.execute(insert_query)
            except Exception as ex:
                LOGGER.warning(str(ex))
                raise ex

    def upsert_row(self, row, keys, table_name):
        """
        Upsert row from SQL table, if there are matching records in the table
        with same value in keys columns they get updated, else creates new record.

        Args:
            row (dict): dictionary with keys as column names
            keys (list): column names to use as keys for updating only matching rows
            table_name (str): output database table name
        """

        condition_exists = " AND ".join(
            [f"{k} = {_value_to_str(row[k])}" if not pd.isna(row[k]) else f"{k} IS NULL" for k in keys]
        )

        exists = int(self._engine.execute(f"SELECT COUNT(1) FROM {table_name} WHERE {condition_exists}").first()[0])

        if exists:
            self.update_row(row, keys, table_name)
        else:
            self.write_row(row, table_name)

        return "UPDATE" if exists else "CREATE"

    def execute(self, query: str) -> LegacyCursorResult:
        return self._engine.execute(query)
