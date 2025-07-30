from typing import Optional, TypeVar, Generic

from resource2 import TaskStageResource
from utils.annotation import frozen_attrs


@frozen_attrs("step_name", "func", "successors", "predecessors")
class StepNode:
    def __init__(self, step_name: str, func: callable):
        self.step_name = step_name
        self.successors = set()
        self.predecessors = set()
        self.func: callable = func

    def addSuccessor(self, *successors: "StepNode") -> None:
        """添加后驱节点（自动处理双向关联）"""
        for successor in successors:
            if not isinstance(successor, StepNode):
                raise TypeError(
                    f"Successor must be a StepNode, got {type(successor).__name__}"
                )
            self.successors.add(successor)
            # 维护双向关联：在后驱节点中添加当前节点为前驱
            successor.addPredecessor(self)

    def addPredecessor(self, *predecessors: "StepNode") -> None:
        """添加前驱节点（自动处理双向关联）"""
        for predecessor in predecessors:
            if not isinstance(predecessor, StepNode):
                raise TypeError(
                    f"Predecessor must be a StepNode, got {type(predecessor).__name__}"
                )
            self.predecessors.add(predecessor)
            # 维护双向关联：在前驱节点中添加当前节点为后驱
            predecessor.addSuccessor(self)


TS = TypeVar("TS", bound=TaskStageResource)


@frozen_attrs("task_name", "task_resource")
class HuibiaoTaskPipeline(Generic[TS]):
    def __init__(self, task_name: str, task_id: str, task_resource: TS):
        self.task_id = task_id
        self.task_name = task_name
        self.task_resource: TS = task_resource
