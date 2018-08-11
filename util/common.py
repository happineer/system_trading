from functools import wraps
import pdb
from util import constant


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


def copy_attr(from_o, to_o, attr_list):
    """object간 속성복사를 수행

    :param from_o: 속성값을 가져올(제공할) object
    :param to_o: 속성값을 복사할 object
    :param attr_list: 속성리스트
    :return:
    """

    try:
        for attr in attr_list:
            val = from_o.__getattribute__(attr)
            to_o.__setattr__(attr, val)
    except Exception:
        raise constant.CopyAttributeException('속성복사도중 예외 발생하였습니다.')
    return to_o
