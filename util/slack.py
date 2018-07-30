from slacker import Slacker
from singleton_decorator import singleton
from util import timeutil
from functools import wraps


@singleton
class Slack(Slacker):
    def __init__(self, token=None):
        self.enable = bool(token)
        if not self.enable:
            return

        # init native Slacker module
        super().__init__(token)

    def is_enable(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not args[0].enable:  # args[0] => self
                return
            return f(*args, **kwargs)
        return wrapper

    @is_enable
    def send_message(self, msg, channel="general"):
        """사용자 msg를 slack message로 전송합니다.

        :param msg:
        :param channel:
        :return:
        """
        self.chat.post_message('#'+channel, msg)

    @is_enable
    def log(self, msg, channel="general"):
        """log msg를 slack message로 전송합니다.
        send_message와 다른점은 msg포맷이 아래와 같이 정해집니다.

        * format
            18/07/26-09:28:32 - Hello, slack!

        :param msg:
        :param channel:
        :return:
        """
        time_str = timeutil.get_time_str()
        msg = "{} - {}".format(time_str, msg)
        self.send_message(msg, channel)
