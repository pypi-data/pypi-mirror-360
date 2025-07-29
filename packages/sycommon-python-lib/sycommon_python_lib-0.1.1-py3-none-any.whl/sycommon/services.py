from typing import Callable, List, Tuple

from sycommon.config.Config import SingletonMeta


class Services(metaclass=SingletonMeta):
    def __init__(self, config):
        self.config = config

    def plugins(self, nacos_service=None, logging_service=None, database_service: Tuple[Callable, str] | List[Tuple[Callable, str]] = None):
        # 注册nacos服务
        if nacos_service:
            nacos_service(self.config)
        # 注册日志服务
        if logging_service:
            logging_service(self.config)
        # 注册数据库服务
        if database_service:
            if isinstance(database_service, tuple):
                # 单个数据库服务
                db_setup, db_name = database_service
                db_setup(self.config, db_name)
            elif isinstance(database_service, list):
                # 多个数据库服务
                for db_setup, db_name in database_service:
                    db_setup(self.config, db_name)
            else:
                raise TypeError(
                    "database_service must be a tuple or a list of tuples")
