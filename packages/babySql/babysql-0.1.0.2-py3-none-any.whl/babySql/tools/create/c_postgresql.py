class PostgreSQLCreateTable:
    """
    创建PostgreSQL表的封装类，支持列定义、主键、索引、外键等
    使用示例：
        creator = PostgreSQLCreateTable(conn, cursor, "users", "用户表")
        creator.column("id").type("SERIAL").primary_key()
        creator.column("username").type("VARCHAR", 50).is_not_null().unique()
        creator.column("email").type("VARCHAR", 100).is_not_null().unique()
        creator.column("country_id").type("INTEGER").foreign_key("countries", "id")
        creator.add_primary_key(["id"])  # 单列主键
        # 或 creator.add_primary_key(["col1", "col2"])  # 复合主键
        creator.build()
    """

    def __init__(self, connect, cursor, table_name: str, table_comment: str = None):
        if type(table_name) is not str:
            raise TypeError("table_name must be a str")
        if table_comment is not None and type(table_comment) is not str:
            raise TypeError("table_comment must be a str")
        self.__connect__ = connect
        self.__cursor__ = cursor
        self.__table_name__ = table_name
        self.__table_comment__ = table_comment
        self.__columns__ = []
        self.__primary_keys__ = []
        self.__unique_constraints__ = []
        self.__foreign_keys__ = []
        self.__indices__ = []

    def column(self, column_name: str):
        """
        初始化字段
        :param column_name: 字段名
        :return: _ColumnBuilder实例
        """
        if type(column_name) is not str:
            raise TypeError("column_name must be a str")
        if any(col["name"] == column_name for col in self.__columns__):
            raise ValueError(f"Column '{column_name}' already exists in table '{self.__table_name__}'")
        column = {
            "name": column_name,
            "type": "VARCHAR",
            "length": None,
            "not_null": False,
            "auto_increment": False,
            "unique": False,
            "comment": None
        }
        self.__columns__.append(column)
        return self._ColumnBuilder(self, column)

    class _ColumnBuilder:
        """
        列属性构建器
        :return:
        """
        _NO_LENGTH_TYPES = {"TEXT", "DATE", "TIMESTAMP", "BOOLEAN", "JSONB", "SERIAL", "BIGSERIAL"}

        def __init__(self, parent, column):
            self._parent = parent
            self._column = column

        def type(self, column_type: str, length: int = None):
            """
            设置列数据类型
            :param column_type: 数据类型 (e.g., "INT", "VARCHAR")
            :param length: 可选长度参数
            :return:
            """
            if type(column_type) is not str:
                raise TypeError("column_type must be a str")
            if type(length) is not int:
                raise TypeError("length must be a int")
            self._column["type"] = column_type.upper()
            # PostgreSQL 中 SERIAL 类型不需要长度
            if column_type.upper() in ("SERIAL", "BIGSERIAL"):
                self._column["auto_increment"] = True
                self._column["not_null"] = True

            if length is not None:
                self._column["length"] = length
            return self

        def is_not_null(self, not_null: bool = True):
            """
            设置NOT NULL约束
            :param not_null: 是否运行为空
            :return:
            """
            if type(not_null) is not bool:
                raise TypeError("not_null must be a bool")
            self._column["not_null"] = not_null
            return self

        def auto_increment(self):
            """
            PostgreSQL 使用 SERIAL 类型处理自增
            :return:
            """
            if self._column["type"] not in ("INTEGER", "INT", "BIGINT"):
                raise ValueError("Auto-increment requires integer type (INT, BIGINT, etc.)")
            # 根据类型选择合适的 SERIAL 类型
            if self._column["type"] in ("BIGINT", "BIGINTEGER"):
                self._column["type"] = "BIGSERIAL"
            else:
                self._column["type"] = "SERIAL"
            self._column["auto_increment"] = True
            self._column["not_null"] = True
            return self

        def unique(self):
            """
            设置唯一约束 (列级)
            :return:
            """
            self._column["unique"] = True
            return self

        def primary_key(self):
            """
            设置为主键 (列级)
            :return:
            """
            self._parent.add_primary_key([self._column["name"]])
            return self

        def comment(self, column_comment: str):
            """
            设置列注释
            :param column_comment: 字段注释
            :return:
            """
            if type(column_comment) is not str:
                raise TypeError("column_comment must be a str")
            self._column["comment"] = column_comment
            return self

        def foreign_key(self, ref_table: str, ref_column: str):
            """
            添加外键约束
            :param ref_table: 表名
            :param ref_column: 字段名
            :return:
            """
            # 外键列自动设置NOT NULL
            if type(ref_table) is not str:
                raise TypeError("ref_table must be a str")
            if type(ref_column) is not str:
                raise TypeError("ref_column must be a str")
            self._column["not_null"] = True
            self._parent.add_foreign_key(self._column["name"], ref_table, ref_column)
            return self

    def add_primary_key(self, columns: list):
        """
        添加主键 (支持复合主键)
        :param columns: 主键列名列表
        :return:
        """
        if type(columns) is not list:
            raise TypeError("columns must be a list")
        if not columns:
            raise ValueError("Primary key must include at least one column")
        # 验证所有列都存在
        for col in columns:
            if not any(c["name"] == col for c in self.__columns__):
                raise ValueError(f"Column '{col}' not defined for primary key")
        self.__primary_keys__ = columns
        # 主键列隐式设置NOT NULL
        for col in self.__columns__:
            if col["name"] in columns:
                col["not_null"] = True

    def add_foreign_key(self, column: str, ref_table: str, ref_column: str):
        """
        添加外键约束
        :param column: 当前表列名
        :param ref_table: 引用表名
        :param ref_column: 引用列名
        :return:
        """
        if type(column) is not str:
            raise TypeError("column must be a str")
        if type(ref_table) is not str:
            raise TypeError("ref_table must be a str")
        if type(ref_column) is not str:
            raise TypeError("ref_column must be a str")
        if not any(c["name"] == column for c in self.__columns__):
            raise ValueError(f"Column '{column}' not defined for foreign key")
        # 确保外键列有NOT NULL约束
        for col in self.__columns__:
            if col["name"] == column:
                col["not_null"] = True
                break
        self.__foreign_keys__.append({
            "column": column,
            "ref_table": ref_table,
            "ref_column": ref_column
        })

    def add_unique_constraint(self, columns: list, constraint_name: str = None):
        """
        添加唯一约束
        :param columns: 列名列表
        :param constraint_name: 可选约束名
        :return:
        """
        if type(columns) is not list:
            raise TypeError("columns must be a list")
        if constraint_name is not None and not columns:
            raise ValueError("Unique constraint must include at least one column")
        if not constraint_name:
            constraint_name = f"uq_{self.__table_name__}_{'_'.join(columns)}"
        self.__unique_constraints__.append({
            "columns": columns,
            "name": constraint_name
        })

    def add_index(self, columns: list, index_prefix: str = None, is_group: bool = False, is_unique: bool = False):
        """
        添加索引
        :param columns: 列名列表
        :param index_prefix: 可选索引名
        :param is_group: 是否是复合索引
        :param is_unique: 是否是唯一索引
        :return:
        """
        if type(columns) is not list:
            raise TypeError("columns must be a list")
        if index_prefix is not None and type(index_prefix) is not str:
            raise TypeError("index_prefix must be a str")
        if type(is_group) is not bool:
            raise TypeError("is_group must be a bool")
        if is_group:
            # 复合索引 - 所有列在一个索引中
            if not index_prefix:
                index_name = f"idx_{self.__table_name__}_{'_'.join(columns)}"
            else:
                index_name = f"{index_prefix}_{'_'.join(columns)}"

            # 确保索引名称唯一
            if any(idx['name'] == index_name for idx in self.__indices__):
                raise ValueError(f"Index name '{index_name}' already exists")

            self.__indices__.append({
                "columns": columns,
                "name": index_name,
                "is_group": True,
                "is_unique": is_unique
            })
        else:
            # 单列索引 - 每个列一个索引
            for col in columns:
                if not index_prefix:
                    index_name = f"idx_{self.__table_name__}_{col}"
                else:
                    index_name = f"{index_prefix}_{col}"

                # 确保索引名称唯一
                if any(idx['name'] == index_name for idx in self.__indices__):
                    raise ValueError(f"Index name '{index_name}' already exists")

                self.__indices__.append({
                    "columns": [col],
                    "name": index_name,
                    "is_group": False,
                    "is_unique": is_unique
                })

    @staticmethod
    def _escape_identifier(identifier: str) -> str:
        """
        转义标识符（表名、列名）
        :param identifier: 数据
        :return:
        """
        if type(identifier) is not str:
            raise TypeError("identifier must be a str")
        return f'"{identifier}"'

    @staticmethod
    def _escape_value(value: str) -> str:
        """
        转义字符串值（用于注释）
        :param value: 数据
        :return:
        """
        if type(value) is not str:
            raise TypeError("value must be a str")
        return value.replace("'", "''")

    def build(self):
        """
        构建并执行CREATE TABLE语句
        :return:
        """
        if not self.__columns__:
            raise ValueError("No columns defined for table creation")

        # 检查自增列是否在主键中
        auto_inc_columns = [col["name"] for col in self.__columns__ if col["auto_increment"]]
        if auto_inc_columns:
            if not self.__primary_keys__ or not all(col in self.__primary_keys__ for col in auto_inc_columns):
                raise ValueError("Auto-increment columns must be part of primary key")

        # 收集所有唯一约束的列（用于避免重复创建索引）
        unique_constraint_columns = set()
        for uc in self.__unique_constraints__:
            # 元组形式存储，保持顺序
            unique_constraint_columns.add(tuple(uc["columns"]))

        # 1. 构建列定义
        column_defs = []
        for col in self.__columns__:
            # 转义列名
            col_name = self._escape_identifier(col['name'])

            # 处理类型和长度
            col_def = f"{col_name} {col['type']}"
            if col["type"] not in self._ColumnBuilder._NO_LENGTH_TYPES and col["length"]:
                col_def += f"({col['length']})"

            # NOT NULL约束
            if col["not_null"]:
                col_def += " NOT NULL"

            # 唯一约束 (列级)
            if col["unique"]:
                col_def += " UNIQUE"
                # 记录单列唯一约束
                unique_constraint_columns.add((col["name"],))

            column_defs.append(col_def)

        # 2. 添加主键约束
        if self.__primary_keys__:
            pk_columns = ", ".join([self._escape_identifier(col) for col in self.__primary_keys__])
            column_defs.append(f"PRIMARY KEY ({pk_columns})")

        # 3. 添加唯一约束 (表级)
        for uc in self.__unique_constraints__:
            columns = ", ".join([self._escape_identifier(col) for col in uc["columns"]])
            constraint_name = self._escape_identifier(uc['name'])
            column_defs.append(f"CONSTRAINT {constraint_name} UNIQUE ({columns})")

        # 4. 添加外键约束
        for fk in self.__foreign_keys__:
            # 生成唯一外键名
            constraint_name = self._escape_identifier(f"fk_{self.__table_name__}_{fk['column']}_{fk['ref_table']}")
            col_name = self._escape_identifier(fk['column'])
            ref_table = self._escape_identifier(fk['ref_table'])
            ref_column = self._escape_identifier(fk['ref_column'])

            column_defs.append(
                f"CONSTRAINT {constraint_name} FOREIGN KEY ({col_name}) "
                f"REFERENCES {ref_table} ({ref_column})"
            )

        # 5. 构建完整SQL
        table_name = self._escape_identifier(self.__table_name__)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        sql += ",\n".join(column_defs)
        sql += "\n);"

        # 6. 执行SQL
        try:
            # 使用连接对象的事务管理
            self.__connect__.autocommit = False

            # 创建表
            self.__cursor__.execute(sql)

            # 7. 添加表注释
            if self.__table_comment__:
                escaped_comment = self._escape_value(self.__table_comment__)
                comment_sql = f"COMMENT ON TABLE {table_name} IS '{escaped_comment}';"
                self.__cursor__.execute(comment_sql)

            # 8. 添加列注释
            for col in self.__columns__:
                if col["comment"]:
                    col_name = self._escape_identifier(col["name"])
                    escaped_comment = self._escape_value(col["comment"])
                    comment_sql = f"COMMENT ON COLUMN {table_name}.{col_name} IS '{escaped_comment}';"
                    self.__cursor__.execute(comment_sql)

            # 9. 创建索引（跳过主键和唯一约束自动创建的索引）
            for idx in self.__indices__:
                # 检查是否由唯一约束自动创建
                idx_columns_tuple = tuple(idx["columns"])
                if idx_columns_tuple in unique_constraint_columns:
                    continue

                # 检查是否完全由主键列组成
                if set(idx["columns"]).issubset(set(self.__primary_keys__)):
                    continue

                index_name = self._escape_identifier(idx['name'])
                columns = ", ".join([self._escape_identifier(col) for col in idx["columns"]])

                # 确定索引类型
                index_type = "UNIQUE INDEX" if idx["is_unique"] else "INDEX"

                # 创建索引SQL
                create_index_sql = f"CREATE {index_type} IF NOT EXISTS {index_name} ON {table_name} ({columns});"
                self.__cursor__.execute(create_index_sql)

            # 提交事务
            self.__connect__.commit()
        except Exception as e:
            # 回滚事务
            self.__connect__.rollback()
            raise RuntimeError(f"Failed to create table '{self.__table_name__}': {str(e)}") from e
        finally:
            # 恢复自动提交设置
            self.__connect__.autocommit = True
