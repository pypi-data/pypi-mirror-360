class SqLiteCreateTable:
    """
    创建SQLite表的封装类，支持列定义、主键、索引、外键等
    使用示例：
        creator = SqLiteCreateTable(conn, cursor, "users")
        creator.column("id").type("INTEGER").primary_key().auto_increment()
        creator.column("username").type("TEXT").is_not_null().unique()
        creator.column("email").type("TEXT").is_not_null().unique()
        creator.column("country_id").type("INTEGER").foreign_key("countries", "id")
        creator.add_primary_key(["id"])  # 单列主键
        # 或 creator.add_primary_key(["col1", "col2"])  # 复合主键
        creator.build()
    """

    def __init__(self, connect, cursor, table_name: str):
        if type(table_name) is not str:
            raise TypeError("table_name must be a str")
        self.__connect__ = connect
        self.__cursor__ = cursor
        self.__table_name__ = table_name
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
            "type": "TEXT",  # SQLite默认使用TEXT类型
            "not_null": False,
            "auto_increment": False,
            "unique": False
        }
        self.__columns__.append(column)
        return self._ColumnBuilder(self, column)

    class _ColumnBuilder:
        """
        列属性构建器
        """
        _NO_LENGTH_TYPES = {"TEXT", "BLOB", "REAL", "INTEGER", "NUMERIC"}

        def __init__(self, parent, column):
            self._parent = parent
            self._column = column

        def type(self, column_type: str):
            """
            设置列数据类型
            :param column_type: 数据类型 (e.g., "INTEGER", "TEXT", "REAL", "BLOB")
            :return:
            """
            if type(column_type) is not str:
                raise TypeError("column_type must be a str")
            self._column["type"] = column_type.upper()
            return self

        def is_not_null(self, not_null: bool = True):
            """
            设置NOT NULL约束
            :param not_null: 是否允许为空
            :return:
            """
            if type(not_null) is not bool:
                raise TypeError("not_null must be a bool")
            self._column["not_null"] = not_null
            return self

        def auto_increment(self):
            """
            设置自增属性
            :return:
            """
            if self._column["type"] != "INTEGER":
                raise ValueError("SQLite auto-increment requires type 'INTEGER'")
            self._column["auto_increment"] = True
            # 自增列隐式设置NOT NULL
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

        def foreign_key(self, ref_table: str, ref_column: str):
            """
            添加外键约束
            :param ref_table: 表名
            :param ref_column: 字段名
            :return:
            """
            if type(ref_table) is not str:
                raise TypeError("ref_table must be a str")
            if type(ref_column) is not str:
                raise TypeError("ref_column must be a str")
            # 外键列自动设置NOT NULL
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
        if constraint_name is not None and type(constraint_name) is not str:
            raise TypeError("constraint_name must be a str")
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
        :return:
        """
        if type(columns) is not list:
            raise TypeError("columns must be a list")
        if index_prefix is not None and type(index_prefix) is not str:
            raise TypeError("index_prefix must be a str")
        if type(is_group) is not bool:
            raise TypeError("is_group must be a bool")
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

    def build(self):
        """
        构建并执行CREATE TABLE语句
        :return:
        """
        if not self.__columns__:
            raise ValueError("No columns defined for table creation")
        # 检查自增列是否在主键中
        auto_inc__columns__ = [col["name"] for col in self.__columns__ if col["auto_increment"]]
        if auto_inc__columns__:
            if not self.__primary_keys__ or not all(col in self.__primary_keys__ for col in auto_inc__columns__):
                raise ValueError("Auto-increment columns must be part of primary key")
            if len(auto_inc__columns__) > 1:
                raise ValueError("SQLite only supports one auto-increment column per table")
        # 1. 构建列定义
        column_defs = []
        for col in self.__columns__:
            col_def = f"{col['name']} {col['type']}"
            # 自增属性 (SQLite使用AUTOINCREMENT)
            if col["auto_increment"]:
                col_def += " PRIMARY KEY AUTOINCREMENT"
            else:
                # NOT NULL约束
                if col["not_null"]:
                    col_def += " NOT NULL"
                # 唯一约束 (列级)
                if col["unique"]:
                    col_def += " UNIQUE"
            column_defs.append(col_def)
        # 2. 添加主键约束 (如果不是自增主键)
        if self.__primary_keys__ and not auto_inc__columns__:
            pk__columns__ = ", ".join([col for col in self.__primary_keys__])
            column_defs.append(f"PRIMARY KEY ({pk__columns__})")
        # 3. 添加唯一约束 (表级)
        for uc in self.__unique_constraints__:
            columns = ", ".join([col for col in uc["columns"]])
            column_defs.append(f"CONSTRAINT {uc['name']} UNIQUE ({columns})")
        # 4. 添加外键约束 (SQLite不支持命名外键约束)
        for fk in self.__foreign_keys__:
            column_defs.append(
                f"FOREIGN KEY ({fk['column']}) "
                f"REFERENCES {fk['ref_table']} ({fk['ref_column']})"
            )
        # 5. 构建完整SQL
        sql = f"CREATE TABLE IF NOT EXISTS {self.__table_name__} (\n"
        sql += ",\n".join(column_defs)
        sql += "\n);"
        # 6. 执行SQL
        try:
            self.__cursor__.execute(sql)
            self.__connect__.commit()
        except Exception as e:
            self.__connect__.rollback()
            raise RuntimeError(f"Failed to create table '{self.__table_name__}': {str(e)}") from e
        # 7. 创建索引 (SQLite索引需要单独创建)
        for idx in self.__indices__:
            columns = ", ".join([col for col in idx["columns"]])
            idx_sql = f"CREATE INDEX IF NOT EXISTS {idx['name']} ON {self.__table_name__} ({columns});"
            try:
                self.__cursor__.execute(idx_sql)
                self.__connect__.commit()
            except Exception as e:
                self.__connect__.rollback()
                raise RuntimeError(f"Failed to create index '{idx['name']}': {str(e)}") from e
