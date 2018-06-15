
from util import strutil
from kiwoom.tr_post import PostFn
from kiwoom import constant
import pdb


class TrManager():
    def __init__(self, kw):
        self.kw = kw
        self.tr_ret_data = None
        self.tr_continue = None
        self.tr_post = PostFn(self)

    def opt10080(self, rqname, code, tick, screen_no, limit=0):
        """
        특정 주식종목의 분봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param tick: str - 분단위(1, 3, 5, 10, 15, 30, 45, 60)
        :param screen_no: str - 화면번호
        :param limit: str - 반복 request 제한 횟수
        :return:
        """
        self.tr_ret_data = []

        def tr_process(rqname, code, next):
            self.kw._set_input_value("종목코드", code)
            self.kw._set_input_value("틱범위", tick)
            self.kw._set_input_value("수정주가구분", "0")
            self.kw._comm_rq_data(rqname, "opt10080", next, screen_no)  # lock event loop

        tr_process(rqname, code, 0)
        for _ in range(limit):
            tr_process(rqname, code, 2)
        return self.tr_ret_data  # data set when post_tr_function

    def opt10081(self, rqname, code, date, screen_no, limit=0):
        """
        특정 주식종목의 일봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param date: str - YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param screen_no: str - 화면번호
        :param limit: str - 반복 request 제한 횟수
        :return:
        """
        self.tr_ret_data = []

        def tr_process(rqname, code, next):
            self.kw._set_input_value("종목코드", code)
            self.kw._set_input_value("기준일자", date)
            self.kw._set_input_value("수정주가구분", "0")
            self.kw._comm_rq_data(rqname, "opt10081", next, screen_no)  # lock event loop

        tr_process(rqname, code, 0)
        for _ in range(limit):
            tr_process(rqname, code, 2)
        return self.tr_ret_data  # data set when post_tr_function

    def opt10082(self, rqname, code, s_date, e_date, screen_no, limit=0):
        """
        특정 주식종목의 주봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param s_date: str - 기준일자. YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param e_date: str - 끝일자.   YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param screen_no: str - 화면번호
        :param limit: str - 반복 request 제한 횟수
        :return:
        """
        self.tr_ret_data = []

        def tr_process(rqname, code, next):
            self.kw._set_input_value("종목코드", code)
            self.kw._set_input_value("기준일자", s_date)
            self.kw._set_input_value("끝일자", e_date)
            self.kw._set_input_value("수정주가구분", "0")
            self.kw._comm_rq_data(rqname, "opt10082", next, screen_no)  # lock event loop

        tr_process(rqname, code, 0)
        for _ in range(limit):
            tr_process(rqname, code, 2)
        return self.tr_ret_data  # data set when post_tr_function

    def opt10083(self, rqname, code, s_date, e_date, screen_no, limit=0):
        """
        특정 주식종목의 월봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param s_date: str - 기준일자. YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param e_date: str - 끝일자.   YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param screen_no: str - 화면번호
        :param limit: str - 반복 request 제한 횟수
        :return:
        """
        self.tr_ret_data = []

        def tr_process(rqname, code, next):
            self.kw._set_input_value("종목코드", code)
            self.kw._set_input_value("기준일자", s_date)
            self.kw._set_input_value("끝일자", e_date)
            self.kw._set_input_value("수정주가구분", "0")
            self.kw._comm_rq_data(rqname, "opt10083", next, screen_no)  # lock event loop

        tr_process(rqname, code, 0)
        for _ in range(limit):
            tr_process(rqname, code, 2)
        return self.tr_ret_data  # data set when post_tr_function

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, _1, _2, _3, _4):
        """
        Kiwoom Receive TR Callback, 서버통신 후 데이터를 받은 시점을 알려준다.
        조회요청 응답을 받거나 조회데이터를 수신했을 때 호출됩니다.
        requestName과 trCode는 commRqData()메소드의 매개변수와 매핑되는 값 입니다.
        조회데이터는 이 이벤트 메서드 내부에서 getCommData() 메서드를 이용해서 얻을 수 있습니다.
        :param screen_no: string - 화면번호(4자리)
        :param rqname: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :param trcode: string - TRansaction name
        :param record_name: string - Record name
        :param next: string - 연속조회유무 ('0': 남은 데이터 없음, '2': 남은 데이터 있음)
        """
        try:
            post_fn = self.tr_post.fn_table[rqname]
            post_fn(trcode, rqname)
        except constant.NotDefinePostFunction as e:
            print(e)

        self.kw.evt_loop.exit()  # release event loop

    def post_opt10080(self, trcode, rqname):
        data = self.kw._get_comm_data_ex(trcode, '주식분봉차트조회')
        f = ["현재가", "거래량", "체결시간", "시가", "고가", "저가", "수정주가구분", "수정비욜",
             "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

        for d in data:
            stock_data = {"현재가": 0, "거래량": 0, "체결시간": None, "시가": 0, "고가": 0, "저가": 0}
            for field, val in zip(f, [_.strip() for _ in d]):
                if field in stock_data:
                    stock_data[field] = strutil.convert_data(field, val)
            self.tr_ret_data.append(stock_data)

    def post_opt10081(self, trcode, rqname):
        data = self.kw._get_comm_data_ex(trcode, '주식일봉차트조회')
        f = ["종목코드", "현재가", "거래량", "거래대금", "일자", "시가", "고가", "저가",
             "수정주가구분", "수정비욜", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

        for d in data:
            stock_data = {"종목코드": 0, "현재가": 0, "거래량": 0, "거래대금": 0, "일자": None, "시가": 0, "고가": 0, "저가": 0}
            for field, val in zip(f, [_.strip() for _ in d]):
                if field in stock_data:
                    stock_data[field] = strutil.convert_data(field, val)
            self.tr_ret_data.append(stock_data)

    def post_opt10082(self, trcode, rqname):
        data = self.kw._get_comm_data_ex(trcode, '주식주봉차트조회')
        f = ["현재가", "거래량", "거래대금", "일자", "시가", "고가", "저가",
             "수정주가구분", "수정비욜", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

        for d in data:
            stock_data = {"현재가": 0, "거래량": 0, "거래대금": 0, "일자": None, "시가": 0, "고가": 0, "저가": 0}
            for field, val in zip(f, [_.strip() for _ in d]):
                if field in stock_data:
                    stock_data[field] = strutil.convert_data(field, val)
            self.tr_ret_data.append(stock_data)

    def post_opt10083(self, trcode, rqname):
        data = self.kw._get_comm_data_ex(trcode, '주식월봉차트조회')
        f = ["현재가", "거래량", "거래대금", "일자", "시가", "고가", "저가",
             "수정주가구분", "수정비욜", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

        for d in data:
            stock_data = {"현재가": 0, "거래량": 0, "거래대금": 0, "일자": None, "시가": 0, "고가": 0, "저가": 0}
            for field, val in zip(f, [_.strip() for _ in d]):
                if field in stock_data:
                    stock_data[field] = strutil.convert_data(field, val)
            self.tr_ret_data.append(stock_data)
