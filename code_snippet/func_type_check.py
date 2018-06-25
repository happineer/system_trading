import pdb
from functools import wraps


def type_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        params = args[1:]
        for i, var_info in enumerate(f.__annotations__.items()):
            var_name, var_type = var_info
            if i < len(params):
                val = params[i]
            elif var_name in kwargs:
                val = kwargs[var_name]
            else:
                continue
            if not isinstance(val, var_type):
                raise Exception("{}'s type is not matched with {}".format(var_name, str(var_type)))
        ret = f(*args, **kwargs)
        return ret
    return wrapper


class MyCls(object):
    def __init__(self):
        pass

    @type_check
    def foo(self, name: str, age: int=0):
        print("hello")
        return "hello"


my_cls = MyCls()
ret = my_cls.foo('sjh', age=33)
print("ret: {}".format(ret))