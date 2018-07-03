
class PostFn():
    def __init__(self, tr_mgr):
        self.fn_table = {
            "고저PER": tr_mgr.post_opt10026,
            "주식분봉": tr_mgr.post_opt10080,
            "주식일봉": tr_mgr.post_opt10081,
            "주식주봉": tr_mgr.post_opt10082,
            "주식월봉": tr_mgr.post_opt10083,
            "주식중복조회": tr_mgr.post_optkwfid
        }
