from huibiao_framework.utils.meta_class import OsAttrMeta
from dotenv import load_dotenv

load_dotenv(".env")


class TaskConfig(metaclass=OsAttrMeta):
    TASK_RESOURCE_DIR: str = "/task_resource"
