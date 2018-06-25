from functools import wraps
import pdb


def type_check(f):
    """
    함수의 인자 type을 annotation을 명시한 경우, type check해주는 decorator
    :param f:
    :return:
    """
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
