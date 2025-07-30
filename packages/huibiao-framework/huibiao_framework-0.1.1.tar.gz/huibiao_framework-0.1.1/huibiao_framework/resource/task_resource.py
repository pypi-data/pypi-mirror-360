import os
from typing import TypeVar, Type, List

from huibiao_framework.config import TaskConfig
from huibiao_framework.utils.annotation import frozen_attrs
from .file_operator import FileOperator
from .resource import BatchFileResource, SingleFileResource, Resource

F = TypeVar("F", bound=FileOperator)
R = TypeVar("R", bound=Resource)


@frozen_attrs("task_dir", "task_id", "resource_list")
class TaskResource:
    def __init__(self, task_id: str):
        self.task_dir = os.path.join(TaskConfig.TASK_RESOURCE_DIR, task_id)
        self.task_id = task_id
        self.resource_list: List[R] = []

    def genSingleFileResource(
        self, name, operator_cls: Type[F], contribute_point: float
    ) -> SingleFileResource:
        res = SingleFileResource(
            operator=operator_cls(os.path.join(self.task_dir, name)),
            contribute_point=contribute_point,
        )
        self.resource_list.append(res)
        return res

    def genBatchFileResource(
        self, name, operator_cls: Type[F], contribute_point: float
    ) -> BatchFileResource:
        res = BatchFileResource(
            os.path.join(self.task_dir, name),
            operator_cls=operator_cls,
            contribute_point=contribute_point,
        )
        self.resource_list.append(res)
        return res

    def load(self):
        for r in self.resource_list:
            r.load()

    def save(self):
        for r in self.resource_list:
            r.save()

    @staticmethod
    def validate_task(cls: type):
        """
        类装饰器，包装 __init__ 方法以验证 contribute_point 总和是否为1
        """
        original_init = cls.__init__

        def wrapped_init(self, *args, **kwargs):
            # 调用原始 __init__
            original_init(self, *args, **kwargs)

            # 校验 resource_list 中 contribute_point 的总和是否为1（允许浮点误差）
            total_contribute_point = sum(r.contribute_point for r in self.resource_list)
            if not (0.999 <= total_contribute_point <= 1.001):
                raise ValueError(
                    f"贡献点总和必须为1，当前总和为 {total_contribute_point:.3f}"
                )

        cls.__init__ = wrapped_init
        return cls
