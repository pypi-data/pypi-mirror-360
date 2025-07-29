from babySql.class_methods import MariaDB
from babySql.class_methods import MySQL
from babySql.class_methods import SqLite
from babySql.class_methods import PostgreSQL


class BabySql:
    def __new__(cls, dt_type, host=None, port=None, user=None, passwd=None, db=None, max_connections=50):
        """
        统一数据库访问接口 - 实例化时返回相应的数据库连接类
        :param dt_type: 数据库类型 ("MySQL", "SqLite", "MariaDB", "PostgreSQL")
        :param host: 数据库主机地址 (MySQL/MariaDB/PostgreSQL 需要)
        :param port: 数据库端口 (MySQL/MariaDB/PostgreSQL 需要)
        :param user: 数据库用户名 (MySQL/MariaDB/PostgreSQL 需要)
        :param passwd: 数据库密码 (MySQL/MariaDB/PostgreSQL 需要)
        :param db: 数据库名称或SQLite文件路径
        :param max_connections: 连接池最大连接数
        :return: 相应的数据库连接类实例
        """
        dt_type = dt_type.lower()

        if dt_type == "mysql":
            return MySQL(
                host=host,
                port=port,
                user=user,
                passwd=passwd,
                db=db,
                max_connections=max_connections
            )
        elif dt_type == "mariadb":
            return MariaDB(
                host=host,
                port=port,
                user=user,
                passwd=passwd,
                db=db,
                max_connections=max_connections
            )
        elif dt_type == "postgresql":
            return PostgreSQL(
                host=host,
                port=port,
                user=user,
                passwd=passwd,
                db=db,
                max_connections=max_connections
            )
        elif dt_type == "sqlite":
            return SqLite(
                db=db,
                max_connections=max_connections
            )
        else:
            raise ValueError(f"不支持的数据库类型: {dt_type}")
