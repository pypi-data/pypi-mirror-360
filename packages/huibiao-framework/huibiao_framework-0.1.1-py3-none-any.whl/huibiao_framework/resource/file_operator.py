import os
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from huibiao_framework.utils.annotation import frozen_attrs
from loguru import logger


def ignore_if_path_not_exists(func):
    def wrapper(instance: "FileOperator", *args, **kwargs):
        if not os.path.exists(instance.path):
            logger.info(f"{instance.path} 不存在，忽略")
            return None  # 路径不存在，不执行方法
        return func(instance, *args, **kwargs)  # 路径存在，正常执行

    return wrapper


D = TypeVar("D")


@frozen_attrs("path")
class FileOperator(Generic[D], ABC):
    """
    文件操作抽象类
    """

    def __init__(self, path: str):
        if path is None:
            raise ValueError("Path cannot be None")
        if not path.endswith(self.file_suffix()):
            raise ValueError(f"Path must end with {self.file_suffix()}")

        # 创建目录
        os.makedirs(os.path.dirname(path), exist_ok=True)

        self.path = path
        self.__data: D = None

    @property
    def data(self) -> D:
        """
        获取数据
        """
        return self.get_data()

    @abstractmethod
    def load(self, **kwargs):
        """
        从本地加载文件
        """
        pass

    @abstractmethod
    def save(self, **kwargs):
        """
        保存文件到本地
        """
        pass

    @ignore_if_path_not_exists
    def get_data(self) -> D:
        if self.__data is None:
            self.load()
        return self.__data

    def set_data(self, data: D):
        self.__data = data

    @classmethod
    @abstractmethod
    def file_suffix(cls) -> str:
        """子类必须实现此类方法，对丁文件的后缀名，不能包含点"""
        pass
