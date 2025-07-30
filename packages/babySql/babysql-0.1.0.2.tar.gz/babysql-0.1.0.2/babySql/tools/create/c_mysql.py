class MySQLCreateTable:
    """
    创建MySQL表的封装类，支持列定义、主键、索引、外键等
    使用示例：
        creator = MySQLCreateTable(conn, cursor, "users", "用户表")
        creator.column("id").type("INT").primary_key().auto_increment()
        creator.column("username").type("VARCHAR", 50).is_not_null().unique()
        creator.column("email").type("VARCHAR", 100).is_not_null().unique()
        creator.column("country_id").type("INT").foreign_key("countries", "id")
        creator.add_primary_key(["id"])  # 单列主键
        # 或 creator.add_primary_key(["col1", "col2"])  # 复合主键
        creator.build()
    """

    def __init__(self, connect, cursor, table_name: str, table_comment: str = None, engine: str = "InnoDB",
                 charset: str = "utf8mb4", collate: str = "utf8mb4_unicode_ci"):
        if type(table_name) is not str:
            raise TypeError("table_name must be a str")
        if table_comment is not None and type(table_comment) is not str:
            raise TypeError("table_comment must be a str")
        if type(engine) is not str:
            raise TypeError("engine must be a str")
        if type(charset) is not str:
            raise TypeError("charset must be a str")
        if type(collate) is not str:
            raise TypeError("collate must be a str")
        self.__connect__ = connect
        self.__cursor__ = cursor
        self.__table_name__ = table_name
        self.__table_comment__ = table_comment
        self.__engine__ = engine
        self.__charset__ = charset
        self.__collate__ = collate
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
        if any(col["name"] == column_name for col in self.__columns__):
            raise ValueError(f"Column '{column_name}' already exists in table '{self.__table_name__}'")
        column = {
            "name": column_name,
            "type": "VARCHAR",
            "length": 255,
            "not_null": False,
            "auto_increment": False,
            "unique": False,
            "comment": None
        }
        self.__columns__.append(column)
        return self._ColumnBuilder(self, column)

    class _ColumnBuilder:
        """ 列属性构建器 """
        _NO_LENGTH_TYPES = {"TEXT", "DATE", "DATETIME", "TIMESTAMP", "BLOB", "JSON", "BOOLEAN", "FLOAT", "DOUBLE"}

        def __init__(self, parent, column):
            self._parent = parent
            self._column = column

        def type(self, column_type: str, length: int = None):
            """
            设置列数据类型
            :param column_type: 数据类型 (e.g., "INT", "VARCHAR")
            :param length: 可选长度参数
            """
            self._column["type"] = column_type.upper()
            if length is not None:
                self._column["length"] = length
            return self

        def is_not_null(self, not_null: bool = True):
            """ 设置NOT NULL约束 """
            self._column["not_null"] = not_null
            return self

        def auto_increment(self):
            """ 设置自增属性 """
            if "INT" not in self._column["type"]:
                raise ValueError("Auto-increment requires integer type (INT, BIGINT, etc.)")
            self._column["auto_increment"] = True
            # 自增列隐式设置NOT NULL
            self._column["not_null"] = True
            return self

        def unique(self):
            """ 设置唯一约束 (列级) """
            self._column["unique"] = True
            return self

        def primary_key(self):
            """ 设置为主键 (列级) """
            self._parent.add_primary_key([self._column["name"]])
            return self

        def comment(self, column_comment: str):
            """ 设置列注释 """
            self._column["comment"] = column_comment
            return self

        def foreign_key(self, ref_table: str, ref_column: str):
            """ 添加外键约束 """
            # 外键列自动设置NOT NULL
            self._column["not_null"] = True
            self._parent.add_foreign_key(self._column["name"], ref_table, ref_column)
            return self

    def add_primary_key(self, columns: list):
        """
        添加主键 (支持复合主键)
        :param columns: 主键列名列表
        """
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
        """
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
        """
        if not constraint_name:
            constraint_name = f"uq_{self.__table_name__}_{'_'.join(columns)}"
        self.__unique_constraints__.append({
            "columns": columns,
            "name": constraint_name
        })

    def add_index(self, columns: list, index_prefix: str = None, is_group: bool = False):
        """
        添加索引
        :param columns: 列名列表
        :param index_prefix: 可选索引名
        :param is_group: 是否是复合主键
        """
        if is_group:
            if not index_prefix:
                index_name = f"idx_{self.__table_name__}_{'_'.join(columns)}"
            else:
                index_name = f"{index_prefix}_{'_'.join(columns)}"
            self.__indices__.append({
                "columns": columns,
                "name": index_name
            })
        else:
            for col in columns:
                if not index_prefix:
                    index_name = f"idx_{self.__table_name__}_{col}"
                else:
                    index_name = f"{index_prefix}_{col}"
                self.__indices__.append({
                    "columns": [col],
                    "name": index_name
                })

    @staticmethod
    def _escape_sql_value(value: str) -> str:
        """ 转义SQL值中的特殊字符 """
        return value.replace("'", "''").replace("\\", "\\\\")

    def build(self):
        """ 构建并执行CREATE TABLE语句 """
        if not self.__columns__:
            raise ValueError("No columns defined for table creation")
        # 检查自增列是否在主键中
        auto_inc__columns__ = [col["name"] for col in self.__columns__ if col["auto_increment"]]
        if auto_inc__columns__:
            if not self.__primary_keys__ or not all(col in self.__primary_keys__ for col in auto_inc__columns__):
                raise ValueError("Auto-increment columns must be part of primary key")
        # 1. 构建列定义
        column_defs = []
        for col in self.__columns__:
            col_def = f"`{col['name']}` {col['type']}"
            # 处理需要长度的类型
            if col["type"] not in self._ColumnBuilder._NO_LENGTH_TYPES and "length" in col:
                col_def += f"({col['length']})"
            # 自增属性
            if col["auto_increment"]:
                col_def += " AUTO_INCREMENT"
            # NOT NULL约束
            if col["not_null"]:
                col_def += " NOT NULL"
            # 唯一约束 (列级)
            if col["unique"]:
                col_def += " UNIQUE"
            # 列注释
            if col["comment"]:
                escaped_comment = self._escape_sql_value(col["comment"])
                col_def += f" COMMENT '{escaped_comment}'"
            column_defs.append(col_def)
        # 2. 添加主键约束
        if self.__primary_keys__:
            pk__columns__ = ", ".join([f"`{col}`" for col in self.__primary_keys__])
            column_defs.append(f"PRIMARY KEY ({pk__columns__})")
        # 3. 添加唯一约束 (表级)
        for uc in self.__unique_constraints__:
            columns = ", ".join([f"`{col}`" for col in uc["columns"]])
            column_defs.append(f"CONSTRAINT `{uc['name']}` UNIQUE ({columns})")
        # 4. 添加索引 (表级)
        for idx in self.__indices__:
            if idx['columns'] not in self.__primary_keys__:
                columns = "`, `".join([col for col in idx["columns"]])
                column_defs.append(f"INDEX `{idx['name']}` (`{columns}`)")
        # 5. 添加外键约束
        for fk in self.__foreign_keys__:
            # 生成唯一外键名
            constraint_name = f"fk_{self.__table_name__}_{fk['column']}_{fk['ref_table']}"
            column_defs.append(
                f"CONSTRAINT `{constraint_name}` "
                f"FOREIGN KEY (`{fk['column']}`) "
                f"REFERENCES `{fk['ref_table']}` (`{fk['ref_column']}`)"
            )
        # 6. 构建完整SQL
        sql = f"CREATE TABLE IF NOT EXISTS `{self.__table_name__}` (\n"
        sql += ",\n".join(column_defs)
        sql += "\n)"
        # 7. 添加表注释
        if self.__table_comment__:
            escaped_comment = self._escape_sql_value(self.__table_comment__)
            sql += f" COMMENT='{escaped_comment}'"
        # 8. 字符集和引擎
        sql += f" ENGINE={self.__engine__} DEFAULT CHARSET={self.__charset__} COLLATE={self.__collate__};"
        # 9. 执行SQL
        try:
            self.__cursor__.execute(sql)
            self.__connect__.commit()
        except Exception as e:
            self.__connect__.rollback()
            raise RuntimeError(f"Failed to create table '{self.__table_name__}': {str(e)}") from e
