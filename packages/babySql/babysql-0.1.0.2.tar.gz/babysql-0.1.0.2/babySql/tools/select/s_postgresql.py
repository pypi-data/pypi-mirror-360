from babySql.tools.select.s_base import SQLSelectConditionsBuilderBase


class PostgreSQLSelectConditionsBuilder(SQLSelectConditionsBuilderBase):
    def __init__(self, head_sql, cursor, connect):
        super().__init__(head_sql, cursor, connect)

    def between_and(self, column: str, start, end, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql('"{column}" BETWEEN %s AND %s', [start, end], condition_mode)
        return self

    def equal(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" = %s', [value], condition_mode)
        return self

    def unequal(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" != %s', [value], condition_mode)
        return self

    def equal_greater(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" >= %s', [value], condition_mode)
        return self

    def equal_less(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" <= %s', [value], condition_mode)
        return self

    def greater(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" > %s', [value], condition_mode)
        return self

    def less(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" < %s', [value], condition_mode)
        return self

    def like_start(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" like %s', [f"{value}%"], condition_mode)
        return self

    def like_end(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" like %s', [f"%{value}"], condition_mode)
        return self

    def like(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" like %s', [f"%{value}%"], condition_mode)
        return self

    def not_like_start(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" not like %s', [f"{value}%"], condition_mode)
        return self

    def not_like_end(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" not like %s', [f"%{value}"], condition_mode)
        return self

    def not_like(self, column: str, value, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f'"{column}" not like %s', [f"%{value}%"], condition_mode)
        return self

    def in_(self, column: str, value: list, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(value) is not list:
            raise TypeError('value should be list')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        if type(value) is not list:
            raise TypeError("value must be list")
        dt = ", ".join(['%s'] * len(value))
        sql = "(" + f"{dt}" + ")"
        self._add_sql(f'"{column}" IN {sql}', value, condition_mode)
        return self

    def not_in(self, column: str, value: list, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(value) is not list:
            raise TypeError('value should be list')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        if type(value) is not list:
            raise TypeError("value must be list")
        dt = ", ".join(['%s'] * len(value))
        sql = "(" + f"{dt}" + ")"
        self._add_sql(f'"{column}" NOT IN {sql}', value, condition_mode)
        return self

    def is_null(self, column: str, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f"{column} IS NULL", [], condition_mode)
        return self

    def is_not_null(self, column: str, condition_mode: str):
        if type(column) is not str:
            raise TypeError('column should be str')
        if type(condition_mode) is not str:
            raise TypeError('condition_mode should be str')
        self._add_sql(f"{column} IS NOT NULL", [], condition_mode)
        return self

    def sort(self, column: str or list, direction: str or list = "ASC"):
        # 统一处理为列表格式，方便后续操作
        if isinstance(column, str):
            column = [column]
            direction = [direction] if isinstance(direction, str) else direction
        elif not isinstance(column, list):
            raise TypeError("column must be str or list")
        # 检查字段类型合法性
        for col in column:
            if not isinstance(col, str):
                raise TypeError(f"Column element {col} is not a string")
        # 处理排序方向（统一转大写并验证）
        if isinstance(direction, str):
            direction = [direction] * len(column)
        elif not isinstance(direction, list) or len(direction) != len(column):
            raise ValueError("direction must be str or list with same length as column")
        # 验证每个方向值并转大写
        normalized_dirs = []
        for dir_val in direction:
            if not isinstance(dir_val, str):
                raise TypeError("direction elements must be strings")
            upper_dir = dir_val.upper()
            if upper_dir not in ("ASC", "DESC"):
                raise ValueError(f"Invalid direction: {dir_val}, must be ASC or DESC")
            normalized_dirs.append(upper_dir)
        # 构建PostgreSQL风格的排序SQL（使用双引号包裹字段名）
        sort_parts = [f'"{col}" {dir_}' for col, dir_ in zip(column, normalized_dirs)]
        if self.__sort_sql__:
            self.__sort_sql__ += ", " + ", ".join(sort_parts)
        else:
            self.__sort_sql__ = f" ORDER BY {', '.join(sort_parts)}"
        return self

    def group_by(self, columns: list):
        if type(columns) is not list:
            raise TypeError("columns must be list")
        formatted_columns = ", ".join(columns)
        if self.__group_by_sql__:
            self.__group_by_sql__ += f", {formatted_columns}"
        else:
            self.__group_by_sql__ = f" GROUP BY {formatted_columns}"
        return self

    def having(self, condition: str):
        if type(condition) is not str:
            raise TypeError('condition should be str')
        if self.__having_sql__:
            self.__having_sql__ += f" AND {condition}"
        else:
            self.__having_sql__ = f" HAVING {condition}"
        return self

    def limit(self, offset: int, limit: int):
        if type(offset) is not int:
            raise TypeError('offset should be int')
        if type(limit) is not int:
            raise TypeError('limit should be int')
        self.__limit_sql__ = f" LIMIT {limit} OFFSET {offset}"
        return self
