from .Error import DBException


class Query:
    def __init__(self, table_name: str, schema: str):
        """初始化表名和模式名"""
        self.table_name = table_name
        self.schema = schema

    def _validate_columns(self, columns=None):
        """校验查询列是否为空"""
        if columns is None or not columns:
            raise DBException("SQLSelectError", "查询列表不能为None或空")

    def _build_select(self, columns):
        """构建 SELECT 部分"""
        return f"SELECT {', '.join(columns)}  FROM {self.schema}.{self.table_name}"

    def _parse_condition(self, key: str, value):
        """解析条件键值对，支持单值和多值"""
        operators = ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN", "BETWEEN"]
        for op in operators:
            if key.endswith(op):
                field = key[: -len(op)].strip()
                if op == "IN":
                    if isinstance(value, (list, tuple)):
                        if not value:
                            raise DBException(
                                "SQLConditionError", "IN 运算符的值不能为空列表或元组"
                            )
                        placeholders = ", ".join(["%s"] * len(value))
                        return f"{field} {op} ({placeholders})", value
                    else:
                        return f"{field} {op} %s", [value]
                elif op == "BETWEEN":
                    if not isinstance(value, (list, tuple)) or len(value) != 2:
                        raise DBException(
                            "SQLConditionError",
                            "BETWEEN 运算符的值必须为包含两个元素的列表或元组",
                        )
                    return f"{field} {op} %s AND %s", value
                else:
                    if isinstance(value, (list, tuple)):
                        placeholders = ", ".join(["%s"] * len(value))
                        return f"{field} IN ({placeholders})", value
                    else:
                        return f"{field} {op} %s", [value]
        raise DBException("SQLConditionError", f"不支持的运算符: {key}")

    def _build_where(self, where):
        """构建 WHERE 条件部分，支持嵌套条件"""
        conditions = []
        params = []
        if where is not None:

            def _parse_nested(condition, logic="AND"):
                nested_conditions = []
                nested_params = []
                for key, value in condition.items():
                    if key.lower() in ["and", "or"]:
                        sub_conditions, sub_params = _parse_nested(value, key.upper())
                        nested_conditions.append(f"({sub_conditions})")
                        nested_params.extend(sub_params)
                    else:
                        sub_condition, sub_params = self._parse_condition(key, value)
                        nested_conditions.append(sub_condition)
                        nested_params.extend(sub_params)
                return f" {logic} ".join(nested_conditions), nested_params

            conditions, params = _parse_nested(where)
        return conditions, params

    def _build_order_by(self, orderby=None):
        """构建 ORDER BY 部分"""
        if orderby is not None:
            return f" ORDER BY {orderby}"
        return ""

    def _build_limit_offset(self, limit=None, offset=None):
        """构建 LIMIT 和 OFFSET 部分"""
        limit_offset = []
        if limit is not None:
            limit_offset.append(f" LIMIT {limit}")
        if offset is not None:
            limit_offset.append(f" OFFSET {offset}")
        return "".join(limit_offset)

    def select(self, columns=None, where=None, orderby=None, limit=None, offset=None):
        """生成 SQL 查询语句和参数"""
        self._validate_columns(columns)
        sql = self._build_select(columns)
        conditions, params = self._build_where(where)
        if conditions:
            sql += f" WHERE {conditions}"
        sql += self._build_order_by(orderby)
        sql += self._build_limit_offset(limit, offset)
        return sql, tuple(params)

    def insert(self, data: dict):
        """生成INSERT语句"""
        if not data:
            raise DBException("SQLInsertError", "插入数据不能为空")

        # 构建列名和占位符
        columns = []
        placeholders = []
        params = []
        for key, value in data.items():
            columns.append(key)
            if isinstance(value, (list, tuple)):
                placeholders.append("(%s)" % ", ".join(["%s"] * len(value)))
                params.extend(value)
            else:
                placeholders.append("%s")
                params.append(value)

        sql = f"INSERT INTO {self.schema}.{self.table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        return sql, tuple(params)

    def insert_mul(self, columns: list, data: list):
        """生成INSERT语句"""
        if not data:
            raise DBException("SQLInsertError", "插入数据不能为空")

        for row in data:
            if len(row) != len(columns):
                raise DBException(
                    "SQLInsertError", "每行数据的列数必须与指定的列数一致"
                )

        column_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        values_placeholders = ", ".join([f"({placeholders})"] * len(data))

        params = [val for row in data for val in row]

        sql = f"INSERT INTO {self.schema}.{self.table_name} ({column_str}) VALUES {values_placeholders}"
        return sql, tuple(params)

    def update(self, data: dict, where=None):
        """生成UPDATE语句"""
        if not data:
            raise DBException("SQLUpdateError", "更新数据不能为空")

        # 构建SET子句
        set_clause = []
        params = []
        for key, value in data.items():
            set_clause.append(f"{key} = %s")
            params.append(value)

            # 构建WHERE条件
        sql = f"UPDATE {self.schema}.{self.table_name} SET {', '.join(set_clause)}"
        conditions, where_params = self._build_where(where)
        if conditions:
            sql += f" WHERE {conditions}"
            params.extend(where_params)

        return sql, tuple(params)

    def delete(self, where=None):
        """生成DELETE语句"""
        sql = f"DELETE FROM {self.schema}.{self.table_name}"
        params = []

        # 构建WHERE条件
        conditions, where_params = self._build_where(where)
        if conditions:
            sql += f" WHERE {conditions}"
            params = where_params

        return sql, tuple(params)


if __name__ == "__main__":
    # 示例使用
    table = Table("name", "public")

    try:
        sql, params = table.select(
            **{
                "columns": ["name AS username", "age AS userage"],
                "where": {
                    "and": {
                        "name=": ["zhoubin", "zhangsan"],  # 支持列表
                        "or": {"age>": 20, "age<": 10},
                        "age BETWEEN": [18, 30],
                    }
                },
                "orderby": "name",
                "limit": 1,
            }
        )
        print("SQL 语句:", sql)
        print("参数列表:", params)

        sql, params = table.insert({"name": "test", "age": 20})
        print("SQL 语句:", sql)
        print("参数列表:", params)

        sql, params = table.insert_mul(
            **{"columns": ["name", "age"], "data": [["zhoubin", 28], ["zhangsan", 30]]}
        )
        print("SQL 语句:", sql)
        print("参数列表:", params)

        sql, params = table.update(
            {"name": "test", "age": 20}, {"name=": "test", "age=": 20}
        )
        print("SQL 语句:", sql)
        print("参数列表:", params)

        sql, params = table.delete({"name=": "test", "age=": 20})
        print("SQL 语句:", sql)
        print("参数列表:", params)
    except DBException as e:
        print(f"数据库异常: {e}")
