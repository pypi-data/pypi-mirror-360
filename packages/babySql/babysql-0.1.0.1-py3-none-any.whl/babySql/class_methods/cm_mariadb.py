import pymysql
from dbutils.pooled_db import PooledDB
from babySql.tools import MariaDBSelectConditionsBuilder, MariaDBCreateTable


class MariaDB:
    def __init__(self, host: str, port: int, user: str, passwd: str, db: str = None, max_connections: int = 50):
        """
        babySql for MariaDB
        :param host: 数据库地址
        :param port: 数据库端口
        :param user: 操作用户
        :param passwd: 用户密码
        :param db: 数据库名称
        :param max_connections: 最大连接数
        """
        if type(host) is not str:
            raise TypeError("host should be str")
        if type(port) is not int:
            raise TypeError("port should be int")
        if type(user) is not str:
            raise TypeError("user should be str")
        if type(passwd) is not str:
            raise TypeError("password should be str")
        if type(db) is not str:
            raise TypeError("db should be str")
        if type(max_connections) is not int:
            raise TypeError("max_connections should be int")
        self.__host__ = host
        self.__port__ = port
        self.__user__ = user
        self.__passwd__ = passwd
        self.__db__ = db
        self.__max_connections__ = max_connections
        self.__pool__ = PooledDB(
            creator=pymysql,
            maxconnections=self.__max_connections__,
            **{
                'host': self.__host__,
                'port': self.__port__,
                'user': self.__user__,
                'password': self.__passwd__,
                'database': self.__db__
            }
        )

    def connect_information(self):
        """
        返回数据库连接信息
        :return:
        """
        return {
            "host": self.__host__,
            "port": self.__port__,
            "user": self.__user__,
            "passwd": self.__passwd__,
            "db": self.__db__
        }

    def user_defined_sql(self, sql: str, params: tuple = None):
        """
        运行自定义SQL\n
        在不输入参数: user_defined_sql('select name from user where id = 1')\n
        输入参数: user_defined_sql('select name from user where id = %s', (1))
        :param sql: SQL
        :param params: 参数，输入参数为参数化查询
        :return:
        """
        if type(sql) is not str:
            raise TypeError("sql should be str")
        if params is not None and type(params) is not tuple:
            raise TypeError("params should be tuple")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        row = cursor.fetchall()
        connect.commit()
        cursor.close()
        connect.close()
        return row

    def insert(self, table: str, columns: list, values: list):
        """
        插入数据
        :param table: 表名
        :param columns: 字段
        :param values: 插入数据
        :return:
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        if type(columns) is not list:
            raise TypeError(f"columns {columns} type is not list")
        if type(values) is not list:
            raise TypeError(f"values {columns} type is not list")
        column = "(" + ", ".join(columns) + ")"
        if type(values[0]) is list:
            params = ()
            value_list = []
            for value in values:
                if len(value) == len(columns):
                    for value_s in value:
                        params += (value_s,)
                    value_list.append("(" + ", ".join(["%s" for _ in value]) + ")")
                else:
                    raise ValueError(f"{columns}->{len(columns)} != {value}->{len(value)}")
            values = ", ".join(value_list)
            sql = f"insert into {table} {column} values {values};"
            connect = self.__pool__.connection()
            cursor = connect.cursor()
            cursor.execute(sql, params)
            connect.commit()
            cursor.close()
            connect.close()
            return sql
        else:
            params = ()
            if len(values) == len(columns):
                for value_s in values:
                    params += (value_s,)
                values = "(" + ", ".join(["%s" for _ in values]) + ")"
                sql = f"insert into {table} {column} values {values};"
                connect = self.__pool__.connection()
                cursor = connect.cursor()
                cursor.execute(sql, params)
                connect.commit()
                cursor.close()
                connect.close()
                return sql
            else:
                raise ValueError(f"{columns}->{len(columns)} != {values}->{len(values)}")

    def update(self, table: str, columns_values: dict):
        """
        更新数据
        :param table: 表名
        :param columns_values: 修改的数据
        :return:
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        if type(columns_values) is not dict:
            raise TypeError(f"columns_values {columns_values} type is not dict")
        cvs = ', '.join([f"{k}='{v}'" for k, v in columns_values.items()])
        head_sql = f"UPDATE {table} SET {cvs} "
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        return MariaDBSelectConditionsBuilder(head_sql, cursor, connect)

    def delete(self, table: str):
        """
        删除数据
        :param table: 表名
        :return:
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        head_sql = f"DELETE FROM {table}"
        return MariaDBSelectConditionsBuilder(head_sql, cursor, connect)

    def select(self, table: str, columns: list = None):
        """
        查询数据
        :param table: 表名
        :param columns: 字段名，默认为全部
        :return:
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        if columns is not None and type(columns) is not list:
            raise TypeError(f"columns {columns} type is not list")
        if columns is None:
            columns_str = "*"
        else:
            keywords = [i[0] for i in self.user_defined_sql("SELECT `name` from mysql.help_keyword")]
            add_columns = []
            for i in columns:
                if i.upper() in keywords:
                    add_columns.append(f"`{i}`")
                else:
                    add_columns.append(f"{i}")
            columns_str = ", ".join(add_columns)
        head_sql = f"SELECT {columns_str} FROM {table}"
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        return MariaDBSelectConditionsBuilder(head_sql, cursor, connect)

    def create_table(self, table_name: str, table_comment: str = None):
        """
        创建表\n
        table = create_table("test")\n
        table.column('id').type('int').length(10)\n
        table.column('name').type('varchar').length(100)\n
        table.build()\n
        :param table_name: 表名
        :param table_comment: 表的备注
        :return:
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        if table_name is not None and type(table_comment) is not str:
            raise TypeError("table_comment should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        return MariaDBCreateTable(connect, cursor, table_name, table_comment=table_comment)

    def create_database(self, database_name: str, character: str = "utf8mb4", collate: str = "utf8mb4_general_ci"):
        """
        创建数据库
        :param database_name: 数据库名
        :param character: 字符集
        :param collate: 校对规则
        :return:
        """
        if type(database_name) is not str:
            raise TypeError("database_name should be str")
        if type(character) is not str:
            raise TypeError("character should be str")
        if type(collate) is not str:
            raise TypeError("collate should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET {character} COLLATE {collate}"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def drop_table(self, table_name: str):
        """
        删除表
        :param table_name: 表名
        :return:
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def show_table(self):
        """
        显示数据库中所有表名
        :return:
        """
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"SHOW TABLES;"
        cursor.execute(sql)
        row = cursor.fetchall()
        connect.commit()
        cursor.close()
        connect.close()
        return row

    def show_table_by_database_name(self, name: str):
        """
        显示指定数据库的表
        :param name: 数据库名
        :return:
        """
        if type(name) is not str:
            raise TypeError("name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"SELECT TABLE_NAME AS '表名' FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{name}';"
        cursor.execute(sql)
        row = cursor.fetchall()
        connect.commit()
        cursor.close()
        connect.close()
        return row

    def show_database(self):
        """
        显示所有数据库
        :return:
        """
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"SHOW DATABASES;"
        cursor.execute(sql)
        row = cursor.fetchall()
        connect.commit()
        cursor.close()
        connect.close()
        return row

    def drop_database(self, database_name: str):
        """
        删除数据库
        :param database_name: 数据库名
        :return:
        """
        if type(database_name) is not str:
            raise TypeError("database_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"DROP DATABASE IF EXISTS {database_name}"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def alter_table_name(self, table_name: str, new_table_name: str):
        """
        更改表名
        :param table_name: 现在的表名
        :param new_table_name: 新的表名
        :return:
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        if type(new_table_name) is not str:
            raise TypeError("new_table_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"ALTER TABLE {table_name} RENAME TO {new_table_name}"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def drop_column(self, table_name: str, column: str):
        """
        删除表中的某个字段
        :param table_name: 表名
        :param column: 字段名
        :return:
        """
        if type(column) is not str:
            raise TypeError("column should be str")
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"ALTER TABLE {table_name} DROP {column};"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def alter_column_type(self, table_name: str, column_name: str, column_type: str, length: int,
                          is_not_null: bool = True, is_primary_key: str = False, is_auto_increment: str = False):
        """
        更改表中某字段的类型
        :param table_name: 表名
        :param column_name: 字段名
        :param column_type: 字段类型
        :param length: 长度
        :param is_not_null: 是否为空
        :param is_primary_key: 是否为关键字
        :param is_auto_increment: 是否自增
        :return:
        """
        if type(column_name) is not str:
            raise TypeError("column_name should be str")
        if type(column_type) is not str:
            raise TypeError("column_type should be str")
        if type(length) is not int:
            raise TypeError("length should be int")
        if type(is_not_null) is not bool:
            raise TypeError("is_not_null should be bool")
        if type(is_primary_key) is not bool:
            raise TypeError("is_primary_key should be bool")
        if type(is_auto_increment) is not bool:
            raise TypeError("is_auto_increment should be bool")
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        constraint = ""
        if is_not_null:
            constraint += " NOT NULL"
        if is_primary_key:
            constraint += " PRIMARY KEY"
        if is_auto_increment:
            constraint += " AUTOINCREMENT"
        sql = f"ALTER TABLE {table_name} MODIFY {column_name} {column_type}({length})"
        sql += constraint
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def alter_column_name(self, table_name: str, column_name: str, new_column_name: str, column_type: str, length: int):
        """
        更改表中某字段的名字
        :param new_column_name: 新的字段名
        :param table_name: 表名
        :param column_name: 字段名
        :param column_type: 字段类型
        :param length: 长度
        :return:
        """
        if type(column_name) is not str:
            raise TypeError("column_name should be str")
        if type(new_column_name) is not str:
            raise TypeError("new_column_name should be str")
        if type(column_type) is not str:
            raise TypeError("column_type should be str")
        if type(length) is not int:
            raise TypeError("length should be int")
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"ALTER TABLE {table_name} CHANGE {column_name} {new_column_name} {column_type}({length})"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def add_column(self, table_name: str, column_name: str, column_type: str = "varchar", length: int = 255,
                   is_not_null: bool = True, is_primary_key: str = False, is_auto_increment: str = False,
                   is_first: bool = False):
        """
        向表中新增字段
        :param is_first: True将新加的属性设置为该表的第一个字段,False将新加的字段置于该表其余字段之后
        :param table_name: 表名
        :param column_name: 字段名
        :param column_type: 字段类型
        :param length: 长度
        :param is_not_null: 是否为空
        :param is_primary_key: 是否为关键字
        :param is_auto_increment: 是否自增
        :return:
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        if type(column_name) is not str:
            raise TypeError("column_name should be str")
        if type(column_type) is not str:
            raise TypeError("column_type should be str")
        if type(length) is not int:
            raise TypeError("length should be int")
        if type(is_not_null) is not bool:
            raise TypeError("is_not_null should be bool")
        if type(is_primary_key) is not bool:
            raise TypeError("is_primary_key should be bool")
        if type(is_auto_increment) is not bool:
            raise TypeError("is_auto_increment should be bool")
        if type(is_first) is not bool:
            raise TypeError("is_first should be bool")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        constraint = ""
        if is_not_null:
            constraint += " NOT NULL"
        if is_primary_key:
            constraint += " PRIMARY KEY"
        if is_auto_increment:
            constraint += " AUTOINCREMENT"
        sql = f"ALTER TABLE {table_name} ADD {column_name} {column_type}({length})"
        sql += constraint
        if is_first:
            sql += " FIRST"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def create_index(self, table_name: str, column_name: str, index_name: str):
        """
        创建索引
        :param table_name: 表名
        :param column_name: 列名
        :param index_name: 索引名
        :return:
        """
        if type(column_name) is not str:
            raise TypeError("column_name should be str")
        if type(index_name) is not str:
            raise TypeError("index_name should be str")
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"CREATE INDEX {index_name} ON {table_name} ({column_name});"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def create_unique_index(self, table_name: str, column_name: str, index_name: str):
        """
        创建唯一索引
        :param table_name: 表名
        :param column_name: 列名
        :param index_name: 索引名
        :return:
        """
        if type(column_name) is not str:
            raise TypeError("column_name should be str")
        if type(index_name) is not str:
            raise TypeError("index_name should be str")
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"CREATE UNIQUE INDEX {index_name} ON {table_name} ({column_name});"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def drop_index(self, table_name: str, index_name: str):
        """
        删除索引
        :param table_name: 表名
        :param index_name: 索引名
        :return:
        """
        if type(index_name) is not str:
            raise TypeError("index_name should be str")
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        sql = f"ALTER TABLE {table_name} DROP INDEX {index_name};"
        cursor.execute(sql)
        connect.commit()
        cursor.close()
        connect.close()

    def get_cursor(self):
        """
        返回游标
        :return:
        """
        connect = self.__pool__.connection()
        cursor = connect.cursor()
        return cursor

    def get_connection(self):
        """
        返回连接
        :return:
        """
        connect = self.__pool__.connection()
        return connect

    def show_columns(self, database: str, table: str):
        """
        获取某张表的所有字段
        :param database: 数据库名
        :param table: 表名
        :return:
        """
        if type(database) is not str:
            raise TypeError("database should be str")
        if type(table) is not str:
            raise TypeError("table should be str")
        columns = ["COLUMN_NAME", "DATA_TYPE"]
        dt = self.select("INFORMATION_SCHEMA.COLUMNS", columns) \
            .equal("TABLE_SCHEMA", database, "and").equal("TABLE_NAME", table, "and").run()
        return dt

    def close(self):
        self.__pool__.close()
