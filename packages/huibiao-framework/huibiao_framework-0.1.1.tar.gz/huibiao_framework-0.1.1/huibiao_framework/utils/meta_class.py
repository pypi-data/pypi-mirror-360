import os


class ConstantClassMeta(type):
    """
    对子类也生效的元类
    """

    def __setattr__(cls, name, value):
        # 检查属性是否已存在且非特殊属性
        if hasattr(cls, name) and not name.startswith("__"):
            raise AttributeError(
                f"The property '{name}' of the constant class {cls.__name__} is not allowed to be modified."
            )

    def __call__(cls, *args, **kwargs):
        raise TypeError(f"The constant class {cls.__name__} cannot be instantiated.")


class ConstantClass(metaclass=ConstantClassMeta):
    pass


class OsAttrMeta(type(ConstantClass), type):
    def __new__(cls, name, bases, attrs):
        for attr in attrs["__annotations__"]:
            # 从环境变量中获取值，全大写
            attrs[attr] = os.getenv(attr.upper(), attrs.get(attr, None))
        return super().__new__(cls, name, bases, attrs)
