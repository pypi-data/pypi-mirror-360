import abc
from abc import ABC


class SQLSelectConditionsBuilderBase(ABC):
    def __init__(self, head_sql, cursor, connect):
        """
        初始化SQL查询条件构建器基类

        Args:
            head_sql: SQL查询语句的头部部分（SELECT子句和FROM子句）
            cursor: 数据库游标对象，用于执行SQL语句
            connect: 数据库连接对象，用于提交事务和关闭连接
        """
        self.__cursor__ = cursor
        self.__connect__ = connect
        self.__head_sql__ = head_sql
        self.__sort_sql__ = ""
        self.__group_by_sql__ = ""
        self.__limit_sql__ = ""
        self.__having_sql__ = ""
        self.__and_where_clauses__ = []
        self.__or_where_clauses__ = []

    @abc.abstractmethod
    def between_and(self, column: str, start: str, end: str, condition_mode: str):
        """
        构建介于两者之间的单表并列查询条件
        :param column: 字段名
        :param start: 开始位置
        :param end: 结束位置
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def equal(self, column: str, value: str, condition_mode: str):
        """
        构建等于的单表并列查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def unequal(self, column: str, value: str, condition_mode: str):
        """
        构建不等于的单表并列查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def equal_greater(self, column: str, value: str, condition_mode: str):
        """
        构建大于等于的单表并列查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def equal_less(self, column: str, value: str, condition_mode: str):
        """
        构建小于等于的单表并列查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def greater(self, column: str, value: str, condition_mode: str):
        """
        构建大于的单表并列查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def less(self, column: str, value: str, condition_mode: str):
        """
        构建小于的单表并列查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def like_start(self, column: str, value: str, condition_mode: str):
        """
        构建以指定值开头的模糊查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def like_end(self, column: str, value: str, condition_mode: str):
        """
        构建以指定值结尾的模糊查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def like(self, column: str, value: str, condition_mode: str):
        """
        构建包含指定值的模糊查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def not_like_start(self, column: str, value: str, condition_mode: str):
        """
        构建不以指定值开头的模糊查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def not_like_end(self, column: str, value: str, condition_mode: str):
        """
        构建不以指定值结尾的模糊查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def not_like(self, column: str, value: str, condition_mode: str):
        """
        构建不包含指定值的模糊查询条件
        :param column: 字段名
        :param value: 值
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def in_(self, column: str, value: list, condition_mode: str):
        """
        构建IN查询条件
        :param column: 字段名
        :param value: 值列表
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def not_in(self, column: str, value: list, condition_mode: str):
        """
        构建NOT IN查询条件
        :param column: 字段名
        :param value: 值列表
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def is_null(self, column: str, condition_mode: str):
        """
        构建IS NULL查询条件
        :param column: 字段名
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def is_not_null(self, column: str, condition_mode: str):
        """
        构建IS NOT NULL查询条件
        :param column: 字段名
        :param condition_mode: 条件类型：and，or
        :return:
        """
        pass

    @abc.abstractmethod
    def sort(self, column: str or list, direction: str or list = "ASC"):
        """
        添加排序条件
        :param column: 排序字段名
        :param direction: 排序方向，ASC（升序）或DESC（降序），默认为ASC
        :return:
        """
        pass

    @abc.abstractmethod
    def group_by(self, columns: list):
        """
        添加分组条件
        :param columns: 分组字段列表
        :return:
        """
        pass

    @abc.abstractmethod
    def having(self, condition: str):
        """
        添加HAVING条件
        :param condition: HAVING子句的条件表达式
        :return:
        """
        pass

    @abc.abstractmethod
    def limit(self, offset: int, limit: int):
        """
        添加LIMIT和OFFSET子句，用于分页
        :param offset: 偏移量，表示从第几条记录开始返回
        :param limit: 返回的记录数量上限
        :return:
        """
        pass

    def _add_sql(self, sql: str, params: list, condition_mode: str):
        """
        将构建的SQL添加到指定列表
        :param sql: SQL语句
        :param params: 参数
        :param condition_mode: 条件类型：and，or
        :return:
        """
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        if type(sql) is not str:
            raise TypeError('sql should be str')
        if type(params) is not list:
            raise TypeError('params should be list')
        if condition_mode.lower() == "and":
            self.__and_where_clauses__.append([sql, params])
        elif condition_mode.lower() == "or":
            self.__or_where_clauses__.append([sql, params])
        else:
            raise ValueError("condition_mode must be 'and' or 'or'")

    def page(self, page: int, page_size: int):
        """
        分页便捷方法
        :param page: 页码，从0开始
        :param page_size: 每页记录数
        :return:
        """
        if type(page) is not int:
            raise TypeError('page should be int')
        if type(page_size) is not int:
            raise TypeError('page_size should be int')
        return self.limit(page * page_size, page_size)

    def _build_where_clause(self):
        """
        构建WHERE子句
        :return: WHERE子句字符串和参数列表
        """
        conditions = []
        params = []
        if self.__and_where_clauses__:
            and_conditions = " AND ".join([c[0] for c in self.__and_where_clauses__])
            for c in self.__and_where_clauses__:
                if len(c[1]) > 0:
                    params.extend(c[1])
            conditions.append(f"({and_conditions})")
        if self.__or_where_clauses__:
            or_conditions = " OR ".join([c[0] for c in self.__or_where_clauses__])
            conditions.append(f"({or_conditions})")
            for c in self.__or_where_clauses__:
                if len(c[1]) > 0:
                    params.extend(c[1])
        where_clause = " AND ".join(conditions) if conditions else ""
        return where_clause, params

    def run(self):
        """
        执行构建好的SQL查询
        :return: 查询结果集
        """
        where_clause, params = self._build_where_clause()
        where_clause = f"WHERE {where_clause}" if where_clause else ""
        # 构建完整SQL语句
        if self.__sort_sql__ != "":
            sql = f"{self.__head_sql__} {where_clause} {self.__sort_sql__} {self.__limit_sql__};"
        elif self.__group_by_sql__ != "":
            sql = f"{self.__head_sql__} {where_clause} {self.__group_by_sql__} {self.__limit_sql__};"
        else:
            sql = f"{self.__head_sql__} {where_clause} {self.__limit_sql__};"
        # 执行SQL
        self.__cursor__.execute(sql, params)
        row = self.__cursor__.fetchall()
        self.__connect__.commit()
        self.__cursor__.close()
        self.__connect__.close()
        return row
