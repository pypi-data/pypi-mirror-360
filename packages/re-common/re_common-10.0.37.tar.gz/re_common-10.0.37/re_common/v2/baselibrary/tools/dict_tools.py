class DotDict(dict):
    """
    让字典成为对象 既可以用字典方式访问 也可以用点访问key
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 递归地将嵌套字典转换为 DotDict
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)

    def __getattr__(self, key):
        try:
            value = self[key]
            if isinstance(value, dict):  # 如果值是字典，继续转换为 DotDict
                return DotDict(value)
            return value
        except KeyError:
            raise AttributeError(f"'DotDict' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        if isinstance(value, dict):  # 如果值是字典，转换为 DotDict
            value = DotDict(value)
        self[key] = value

    def to_dict(self):
        """
        将 DotDict 实例转换为普通字典
        """
        result = {}
        for key, value in self.items():
            if isinstance(value, DotDict):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result


def none_to_empty_str(d):
    for k, v in d.items():
        if v is None:
            d[k] = ""
    return d
