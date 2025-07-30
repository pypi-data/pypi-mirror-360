import sqlite3
from sqlite3 import Connection, Cursor
from typing import List, Dict, Any
from babySql.tools import SqLiteSelectConditionsBuilder, SqLiteCreateTable
from dbutils.pooled_db import PooledDB


class SqLite:
    def __init__(self, db: str, max_connections: int = 50):
        """
        babySql for SQLite
        :param db: SQLite数据库文件路径（或":memory:"表示内存数据库）
        :param max_connections: 最大连接数
        """
        self.__database__ = db
        self.__max_connections__ = max_connections
        # SQLite连接池
        self.__pool__ = PooledDB(
            creator=sqlite3,
            maxconnections=self.__max_connections__,
            database=self.__database__,
            check_same_thread=False  # 允许多线程访问
        )

    def connect_information(self):
        """
        返回数据库连接信息
        """
        return {"database": self.__database__}

    def user_defined_sql(self, sql: str, params: tuple = None):
        """
        运行自定义SQL
        :param sql: SQL语句
        :param params: 参数（可选）
        :return: 查询结果
        """
        if type(sql) is not str:
            raise TypeError("sql should be str")
        if params is not None and type(params) is not tuple:
            raise TypeError("params should be tuple")
        conn = self.__pool__.connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            # 如果是SELECT语句，返回结果
            if sql.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                result = cursor.rowcount
            conn.commit()
            return result
        finally:
            cursor.close()
            conn.close()

    def insert(self, table: str, columns: list, values: list) -> int:
        """
        插入数据
        :param table: 表名
        :param columns: 字段列表
        :param values: 值列表
        :return: 最后插入的行ID
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        if not isinstance(columns, list):
            raise TypeError(f"columns must be list, got {type(columns)}")
        if not isinstance(values, list):
            raise TypeError(f"values must be list, got {type(values)}")
        # 构建SQL
        placeholders = ", ".join(["?"] * len(columns))
        columns_str = ", ".join(columns)
        sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        conn = self.__pool__.connection()
        cursor = conn.cursor()
        try:
            # 处理批量插入
            if isinstance(values[0], list):
                cursor.executemany(sql, values)
            else:
                cursor.execute(sql, values)
            conn.commit()
            return cursor.lastrowid  # 返回最后插入的行ID
        finally:
            cursor.close()
            conn.close()

    def update(self, table: str, columns_values: dict):
        """
        更新数据
        :param table: 表名
        :param columns_values: 要更新的字段值字典
        :return: 条件构建器
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        if not isinstance(columns_values, dict):
            raise TypeError(f"columns_values must be dict, got {type(columns_values)}")
        # 构建SET子句
        set_clause = ", ".join([f"{k} = ?" for k in columns_values.keys()])
        head_sql = f"UPDATE {table} SET {set_clause} "
        conn = self.__pool__.connection()
        cursor = conn.cursor()
        return SqLiteSelectConditionsBuilder(head_sql, cursor, conn)

    def delete(self, table: str):
        """
        删除数据
        :param table: 表名
        :return: 条件构建器
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        conn = self.__pool__.connection()
        cursor = conn.cursor()
        head_sql = f"DELETE FROM {table}"
        return SqLiteSelectConditionsBuilder(head_sql, cursor, conn)

    def select(self, table: str, columns: list = None):
        """
        查询数据
        :param table: 表名
        :param columns: 要查询的字段列表（可选）
        :return: 条件构建器
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        if columns is not None and not isinstance(columns, list):
            raise TypeError(f"columns must be list or None, got {type(columns)}")
        # 构建SELECT子句
        columns_str = "*" if columns is None else ", ".join(columns)
        head_sql = f"SELECT {columns_str} FROM {table}"
        conn = self.__pool__.connection()
        cursor = conn.cursor()
        return SqLiteSelectConditionsBuilder(head_sql, cursor, conn)

    def create_table(self, table_name: str):
        """
        创建表
        :param table_name: 表名
        :return: 表创建器
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        conn = self.__pool__.connection()
        cursor = conn.cursor()
        return SqLiteCreateTable(conn, cursor, table_name)

    def drop_table(self, table_name: str):
        """
        删除表
        :param table_name: 表名
        :return:
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        self.user_defined_sql(f"DROP TABLE IF EXISTS {table_name}")

    def show_tables(self) -> List[str]:
        """
        显示数据库中所有表名
        :return: 表名列表
        """
        result = self.user_defined_sql(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in result]

    def table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取表结构信息
        :param table_name: 表名
        :return: 表结构信息列表
        :return:
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        result = self.user_defined_sql(f"PRAGMA table_info({table_name})")
        # 转换为字典列表
        columns = []
        for row in result:
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": bool(row[3]),
                "dflt_value": row[4],
                "pk": bool(row[5])
            })
        return columns

    def create_index(self, table_name: str, columns: list, index_name: str = None, unique: bool = False):
        """
        创建索引
        :param table_name: 表名
        :param columns: 列名列表
        :param index_name: 索引名（可选）
        :param unique: 是否唯一索引
        :return:
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        if not isinstance(columns, list):
            raise TypeError(f"columns must be list, got {type(columns)}")
        if not isinstance(unique, bool):
            raise TypeError("index_name should be str")
        if index_name is not None and not isinstance(index_name, str):
            raise TypeError("index_name should be str")
        if not index_name:
            index_name = f"idx_{table_name}_{'_'.join(columns)}"
        columns_str = ", ".join(columns)
        unique_str = "UNIQUE " if unique else ""
        sql = f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"
        self.user_defined_sql(sql)

    def drop_index(self, index_name: str):
        """
        删除索引
        :param index_name: 索引名
        :return:
        """
        if type(index_name) is not str:
            raise TypeError("index_name should be str")
        self.user_defined_sql(f"DROP INDEX IF EXISTS {index_name}")

    def add_column(self, table_name: str, column_name: str, column_type: str,
                   not_null: bool = False, default_value: Any = None):
        """
        向表中添加列
        :param table_name: 表名
        :param column_name: 列名
        :param column_type: 列类型
        :param not_null: 是否非空
        :param default_value: 默认值
        :return:
        """
        if type(table_name) is not str:
            raise TypeError("table_name should be str")
        if not isinstance(column_name, str):
            raise TypeError("column_name should be str")
        if not isinstance(column_type, str):
            raise TypeError("column_type should be str")
        if not isinstance(not_null, bool):
            raise TypeError("not_null should be bool")
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if not_null:
            sql += " NOT NULL"
        if default_value is not None:
            if isinstance(default_value, str):
                sql += f" DEFAULT '{default_value}'"
            else:
                sql += f" DEFAULT {default_value}"
        self.user_defined_sql(sql)

    def rename_table(self, old_name: str, new_name: str):
        """
        重命名表
        :param old_name: 原表名
        :param new_name: 新表名
        :return:
        """
        if type(old_name) is not str:
            raise TypeError("old_name should be str")
        if type(new_name) is not str:
            raise TypeError("new_name should be str")
        self.user_defined_sql(f"ALTER TABLE {old_name} RENAME TO {new_name}")

    def vacuum(self):
        """
        执行VACUUM操作（优化数据库）
        :return:
        """
        self.user_defined_sql("VACUUM")

    def backup(self, backup_file: str):
        """
        备份数据库
        :param backup_file: 备份文件路径
        :return:
        """
        if type(backup_file) is not str:
            raise TypeError("backup_file should be str")
        conn = self.__pool__.connection()
        try:
            with sqlite3.connect(backup_file) as backup_conn:
                conn.backup(backup_conn)
        finally:
            conn.close()

    def get_cursor(self) -> Cursor:
        """
        获取数据库游标
        :return: SQLite游标对象
        :return:
        """
        conn = self.__pool__.connection()
        return conn.cursor()

    def get_connection(self) -> Connection:
        """
        获取数据库连接
        :return: SQLite连接对象
        :return:
        """
        return self.__pool__.connection()

    def close(self):
        """
        关闭连接池
        :return:
        """
        self.__pool__.close()

    def execute_script(self, script: str):
        """
        执行SQL脚本
        :param script: SQL脚本内容
        :return:
        """
        if type(script) is not str:
            raise TypeError("script should be str")
        conn = self.__pool__.connection()
        try:
            conn.executescript(script)
            conn.commit()
        finally:
            conn.close()

    def get_last_rowid(self, table: str) -> int:
        """
        获取表中最后插入的行ID
        :param table: 表名
        :return: 最后插入的行ID
        """
        if type(table) is not str:
            raise TypeError("table should be str")
        result = self.user_defined_sql(f"SELECT seq FROM sqlite_sequence WHERE name='{table}'")
        return result[0][0] if result else 0

    def foreign_key_check(self, enable: bool = True):
        """
        启用或禁用外键约束检查
        :param enable: 是否启用
        :return:
        """
        if type(enable) is not bool:
            raise TypeError("enable should be bool")
        value = "ON" if enable else "OFF"
        self.user_defined_sql(f"PRAGMA foreign_keys = {value}")

    def integrity_check(self) -> bool:
        """
        执行完整性检查
        :return:
        """
        result = self.user_defined_sql("PRAGMA integrity_check")
        return result[0][0] == "ok"
