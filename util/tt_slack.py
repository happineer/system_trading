from slacker import Slacker
from config import config_manager
from singleton_decorator import singleton
from util import timeutil


@singleton
class TTSlack(object):
    def __init__(self):
        self.slack = Slacker(config_manager.get_slack_token())

    def notify(self, msg, channel='general'):
        """

        :param msg:
        :param channel:
        :return:
        """
        msg = "[{t}]{msg}".format(t=timeutil.get_time(), msg=msg)
        self.slack.chat.post_message(channel, msg)
