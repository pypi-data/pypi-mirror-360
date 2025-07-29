import psycopg2

from .Error import DBException


def db_exception(e_type: str = "ValueError", e_msg: str = "None"):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DBException as e:
                raise e
            except Exception:
                raise DBException(e_type, e_msg)

        return wrapper

    return decorator


class PDBConn:
    @db_exception("DBLinkError", "数据库连接失败")
    def __init__(self, user: str, password: str, host: str, port: int, database: str):
        self.conn = psycopg2.connect(
            user=user, password=password, host=host, port=port, database=database
        )

    def before_connect(self):
        if not self.conn:
            raise DBException("DBConnIsNone", "数据库未连接")

    @db_exception("DBConnPingError", "数据库连接失败")
    def ping(self):
        self.before_connect()
        with self.conn.cursor() as cur:
            cur.execute("SELECT   1")

    @db_exception("DBCommitError", "事务提交失败")
    def commit(self):
        self.before_connect()
        self.conn.commit()

    @db_exception("DBConnCloseError", "数据库连接关闭失败")
    def close(self):
        self.before_connect()
        self.conn.close()
        self.conn = None

    @db_exception("DBConnSelect", "数据库查询失败")
    def select(self, table_name: str, columns: str = "*", where_clause: str = ""):
        self.before_connect()
        with self.conn.cursor() as cur:
            if where_clause:
                sql = f"SELECT {columns} FROM {table_name} WHERE {where_clause}"
            else:
                sql = f"SELECT {columns} FROM {table_name}"
            cur.execute(sql)
            return cur.fetchall()

    @db_exception("DBUpdateError", "数据库更新操作失败")
    def update(self, table_name: str, set_values: dict, where_clause: str):
        self.before_connect()
        set_clause = ", ".join([f"{key} = %s" for key in set_values.keys()])
        values = list(set_values.values())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        with self.conn.cursor() as cur:
            cur.execute(sql, values)

    @db_exception("DBInsertError", "数据库插入操作失败")
    def insert(self, table_name: str, data: dict):
        self.before_connect()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        with self.conn.cursor() as cur:
            cur.execute(sql, values)

    @db_exception("DBDeleteError", "数据库删除操作失败")
    def delete(self, table_name: str, where_clause: str):
        self.before_connect()
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        with self.conn.cursor() as cur:
            cur.execute(sql)

    @db_exception("DBFunctionCallError", "调用数据库函数失败")
    def call_func(self, schema_name: str, f_name: str, params: dict, f_callback):
        self.before_connect()
        param_str = ", ".join([f"%({key})s" for key in params.keys()])
        sql = f"SELECT * FROM {schema_name}.{f_name}({param_str})"
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            result = cur.fetchall()
            return f_callback(result)
