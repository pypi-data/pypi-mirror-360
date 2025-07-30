import os.path
import time
from abc import ABC, abstractmethod
from typing import TypeVar, Type, List, final

from huibiao_framework.execption.execption import FolderResourceAlreadyExistException
from .file_operator import FileOperator
from huibiao_framework.utils.annotation import frozen_attrs
from huibiao_framework.utils.meta_class import ConstantClass


class ResourceStatusTagConstant(ConstantClass):
    DONE = "__DONE"


F = TypeVar("F", bound=FileOperator)


@frozen_attrs("contribute_point")
class Resource(ABC):
    def __init__(self, contribute_point: float):
        self.contribute_point = contribute_point

    @abstractmethod
    def is_completed(self, *args, **kwargs) -> bool:
        """
        该资源是否准备完毕
        """
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def save(self):
        pass


@frozen_attrs("operator")
class SingleFileResource(Resource):
    def __init__(self, operator: F, contribute_point: float):
        super().__init__(contribute_point)
        self.operator: F = operator

    @final
    def is_completed(self, *args, **kwargs) -> bool:
        return os.path.exists(self.operator.__path)

    def load(self, **kwargs):
        if os.path.exists(self.operator.path):
            self.operator.load(**kwargs)

    def save(self, **kwargs):
        self.operator.save(**kwargs)

    @property
    def data(self):
        return self.operator.get_data()

    def set_data(self, data):
        self.operator.set_data(data)


@frozen_attrs("folder", "operator_cls", "operator_list")
class BatchFileResource(Resource):
    def __init__(self, folder, operator_cls: Type[F], contribute_point: float):
        super().__init__(contribute_point)
        os.makedirs(folder, exist_ok=True)
        self.folder = folder
        self.operator_cls: Type[F] = operator_cls
        self.operator_list: List[F] = []

    def __getitem__(self, idx) -> F:
        return self.operator_list[idx]

    def __len__(self):
        return len(self.operator_list)

    @final
    def is_completed(self) -> bool:
        return os.path.exists(os.path.join(self.folder, ResourceStatusTagConstant.DONE))

    @final
    def complete(self):
        if os.path.exists(os.path.exists(os.path.join(self.folder, ResourceStatusTagConstant.DONE))):
            raise FolderResourceAlreadyExistException(f"任务资源{self.folder}已经完成")
        with open(
            os.path.join(self.folder, ResourceStatusTagConstant.DONE),
            "w",
        ) as f:
            local_time = time.localtime(time.time())
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            f.write(formatted_time)  # 往目录下写入一个文件，包含当前时间

    def genAppendPath(self):
        return os.path.join(
            self.folder, f"{len(self)}.{self.operator_cls.file_suffix()}"
        )

    def append(self, data) -> F:
        if self.is_completed():
            raise Exception("已收集完毕，无法添加新的资源文件")
        new_resource_item: Type[F] = self.operator_cls(path=self.genAppendPath())
        new_resource_item.set_data(data)
        self.operator_list.append(new_resource_item)
        return new_resource_item

    def load(self, **kwargs):
        for r in self.operator_list:
            r.load(**kwargs)

    def save(self, **kwargs):
        for r in self.operator_list:
            r.save(**kwargs)
