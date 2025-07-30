import warnings
import functools

# 全局集合，用于记录已警告的函数或类
_warned_once = set()


def deprecated(message=None):
    """
    装饰器：标记函数或类为已废弃，整个进程只发出一次警告。

    Args:
        message (str): 自定义警告信息，默认为 None。
    """

    def decorator(obj):
        # 如果是函数
        if isinstance(obj, type(lambda: None)):
            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                obj_id = id(obj)  # 使用对象的内存地址作为唯一标识
                if obj_id not in _warned_once:
                    default_msg = f"函数 {obj.__name__} 已不建议使用。"
                    warn_msg = f"{default_msg} {message}" if message else default_msg
                    warnings.warn(
                        warn_msg,
                        category=DeprecationWarning,
                        stacklevel=2
                    )
                    _warned_once.add(obj_id)  # 记录已警告
                return obj(*args, **kwargs)

            return wrapper

        # 如果是类
        elif isinstance(obj, type):
            orig_init = obj.__init__

            @functools.wraps(orig_init)
            def new_init(self, *args, **kwargs):
                obj_id = id(obj)
                if obj_id not in _warned_once:
                    default_msg = f"类 {obj.__name__} 已不建议使用。"
                    warn_msg = f"{default_msg} {message}" if message else default_msg
                    warnings.warn(
                        warn_msg,
                        category=DeprecationWarning,
                        stacklevel=2
                    )
                    _warned_once.add(obj_id)  # 记录已警告
                orig_init(self, *args, **kwargs)

            obj.__init__ = new_init
            return obj

        else:
            raise TypeError("此装饰器仅适用于函数和类")

    return decorator
