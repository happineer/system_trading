from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QTime
import json
import time
import pdb
from pprint import pprint
from config import config_manager
import util
from PyQt5.QtCore import Qt


class UiManager():
    def __init__(self, main_ui):
        self.main_ui = main_ui
        self.kw = main_ui.kw
        self.dbm = main_ui.dbm
        self.first_buy_call = True
        self.first_sell_call = True
        self.refresh_strategy_flag = False
        self.refresh_buy_method_flag = False
        self.refresh_sell_method_flag = False
        self.delete_reload = False
        self.status_bar = self.main_ui.statusBar()

        self.init_groups()
        self.set_table_header()
        self.load_strategy()
        self.load_buy_method()
        self.load_sell_method()

        self.init_event()

    def init_groups(self):
        # strategy
        self.chb_trade_group = [
            ('trade_available_01', self.main_ui.chb_trade_01, 'checkbox'),
            ('trade_available_02', self.main_ui.chb_trade_02, 'checkbox'),
            ('trade_available_03', self.main_ui.chb_trade_03, 'checkbox'),
            ('trade_available_04', self.main_ui.chb_trade_04, 'checkbox'),
            ('trade_available_05', self.main_ui.chb_trade_05, 'checkbox')
        ]
        self.te_trade_begin_group = [
            ('trade_begin_01', self.main_ui.te_trade_begin_01, 'timeedit'),
            ('trade_begin_02', self.main_ui.te_trade_begin_02, 'timeedit'),
            ('trade_begin_03', self.main_ui.te_trade_begin_03, 'timeedit'),
            ('trade_begin_04', self.main_ui.te_trade_begin_04, 'timeedit'),
            ('trade_begin_05', self.main_ui.te_trade_begin_05, 'timeedit')
        ]
        self.te_trade_end_group = [
            ('trade_end_01', self.main_ui.te_trade_end_01, 'timeedit'),
            ('trade_end_02', self.main_ui.te_trade_end_02, 'timeedit'),
            ('trade_end_03', self.main_ui.te_trade_end_03, 'timeedit'),
            ('trade_end_04', self.main_ui.te_trade_end_04, 'timeedit'),
            ('trade_end_05', self.main_ui.te_trade_end_05, 'timeedit'),
        ]
        self.cmb_buy_method_group = [
            ('buy_method_01', self.main_ui.cmb_buy_method_01, 'combobox'),
            ('buy_method_02', self.main_ui.cmb_buy_method_02, 'combobox'),
            ('buy_method_03', self.main_ui.cmb_buy_method_03, 'combobox'),
            ('buy_method_04', self.main_ui.cmb_buy_method_04, 'combobox'),
            ('buy_method_05', self.main_ui.cmb_buy_method_05, 'combobox')
        ]
        self.cmb_sell_method_group = [
            ('sell_method_01', self.main_ui.cmb_sell_method_01, 'combobox'),
            ('sell_method_02', self.main_ui.cmb_sell_method_02, 'combobox'),
            ('sell_method_03', self.main_ui.cmb_sell_method_03, 'combobox'),
            ('sell_method_04', self.main_ui.cmb_sell_method_04, 'combobox'),
            ('sell_method_05', self.main_ui.cmb_sell_method_05, 'combobox')
        ]
        self.strategy_groups = [
            self.chb_trade_group,
            self.te_trade_begin_group,
            self.te_trade_end_group,
            self.cmb_buy_method_group,
            self.cmb_sell_method_group
        ]

        # buy method
        self.buy_basic_setting_group = [
            ('max_stock_num', self.main_ui.spb_max_stock_num, 'spinbox'),
            ('max_stock_price', self.main_ui.spb_max_stock_price, 'spinbox'),
            ('buy_cancel_time', self.main_ui.spb_buy_cancel_time, 'spinbox'),
        ]
        self.buy_cmb_condition_group = [
            ('buy_condition_01', self.main_ui.cmb_buy_condition_01, 'combobox'),
            ('buy_condition_02', self.main_ui.cmb_buy_condition_02, 'combobox'),
            ('buy_condition_03', self.main_ui.cmb_buy_condition_03, 'combobox'),
            ('buy_condition_04', self.main_ui.cmb_buy_condition_04, 'combobox'),
            ('buy_condition_05', self.main_ui.cmb_buy_condition_05, 'combobox'),
            ('buy_condition_06', self.main_ui.cmb_buy_condition_06, 'combobox'),
            ('buy_condition_07', self.main_ui.cmb_buy_condition_07, 'combobox')
        ]
        self.buy_chb_condition_group = [
            ('buy_condition_available_01', self.main_ui.chb_buy_condition_01, 'checkbox'),
            ('buy_condition_available_02', self.main_ui.chb_buy_condition_02, 'checkbox'),
            ('buy_condition_available_03', self.main_ui.chb_buy_condition_03, 'checkbox'),
            ('buy_condition_available_04', self.main_ui.chb_buy_condition_04, 'checkbox'),
            ('buy_condition_available_05', self.main_ui.chb_buy_condition_05, 'checkbox'),
            ('buy_condition_available_06', self.main_ui.chb_buy_condition_06, 'checkbox'),
            ('buy_condition_available_07', self.main_ui.chb_buy_condition_07, 'checkbox')
        ]
        self.buy_cmb_theme_group = [
            ('buy_theme_01', self.main_ui.cmb_buy_theme_01, 'combobox'),
            ('buy_theme_02', self.main_ui.cmb_buy_theme_02, 'combobox')
        ]
        self.buy_chb_theme_group = [
            ('buy_theme_available_01', self.main_ui.chb_buy_theme_01, 'checkbox'),
            ('buy_theme_available_02', self.main_ui.chb_buy_theme_02, 'checkbox')
        ]
        # [중요] theme에 대해서는 저장안함
        self.buy_method_groups = [
            self.buy_basic_setting_group,
            self.buy_cmb_condition_group,
            self.buy_chb_condition_group
        ]

        # sell method
        self.sell_basic_setting_group = [
            ('sell_order_cancel_time', self.main_ui.spb_sell_order_cancel_time, 'spinbox'),
            ('end_time_sell', self.main_ui.chb_end_time_sell, 'checkbox'),
            ('sell_max_time_available', self.main_ui.chb_sell_max_time, 'checkbox'),
            ('sell_max_time', self.main_ui.spb_sell_max_time, 'spinbox'),
        ]
        self.sell_chk_profit_group = [
            ('profit_sell_01', self.main_ui.chb_profit_sell_01, 'checkbox'),
            ('profit_sell_02', self.main_ui.chb_profit_sell_02, 'checkbox'),
            ('profit_sell_03', self.main_ui.chb_profit_sell_03, 'checkbox'),
            ('profit_sell_04', self.main_ui.chb_profit_sell_04, 'checkbox'),
        ]
        self.sell_profit_rate_group = [
            ('profit_sell_rate_01', self.main_ui.dspb_profit_sell_rate_01, 'doublespinbox'),
            ('profit_sell_rate_02', self.main_ui.dspb_profit_sell_rate_02, 'doublespinbox'),
            ('profit_sell_rate_03', self.main_ui.dspb_profit_sell_rate_03, 'doublespinbox'),
            ('profit_sell_rate_04', self.main_ui.dspb_profit_sell_rate_04, 'doublespinbox'),
        ]
        self.sell_profit_volumn_group = [
            ('profit_sell_volume_01', self.main_ui.spb_profit_sell_volume_01, 'spinbox'),
            ('profit_sell_volume_02', self.main_ui.spb_profit_sell_volume_02, 'spinbox'),
            ('profit_sell_volume_03', self.main_ui.spb_profit_sell_volume_03, 'spinbox'),
            ('profit_sell_volume_04', self.main_ui.spb_profit_sell_volume_04, 'spinbox'),
        ]
        self.sell_chk_losscut_group = [
            ('losscut_sell_01', self.main_ui.chb_losscut_sell_01, 'checkbox'),
            ('losscut_sell_02', self.main_ui.chb_losscut_sell_02, 'checkbox'),
            ('losscut_sell_03', self.main_ui.chb_losscut_sell_03, 'checkbox'),
            ('losscut_sell_04', self.main_ui.chb_losscut_sell_04, 'checkbox'),
        ]
        self.sell_losscut_rate_group = [
            ('losscut_sell_rate_01', self.main_ui.dspb_losscut_sell_rate_01, 'doublespinbox'),
            ('losscut_sell_rate_02', self.main_ui.dspb_losscut_sell_rate_02, 'doublespinbox'),
            ('losscut_sell_rate_03', self.main_ui.dspb_losscut_sell_rate_03, 'doublespinbox'),
            ('losscut_sell_rate_04', self.main_ui.dspb_losscut_sell_rate_04, 'doublespinbox'),
        ]
        self.sell_losscut_volumn_group = [
            ('losscut_sell_volume_01', self.main_ui.spb_losscut_sell_volume_01, 'spinbox'),
            ('losscut_sell_volume_02', self.main_ui.spb_losscut_sell_volume_02, 'spinbox'),
            ('losscut_sell_volume_03', self.main_ui.spb_losscut_sell_volume_03, 'spinbox'),
            ('losscut_sell_volume_04', self.main_ui.spb_losscut_sell_volume_04, 'spinbox'),
        ]
        self.sell_method_groups = [
            self.sell_basic_setting_group,
            self.sell_chk_profit_group,
            self.sell_profit_rate_group,
            self.sell_profit_volumn_group,
            self.sell_chk_losscut_group,
            self.sell_losscut_rate_group,
            self.sell_losscut_volumn_group
        ]

        # risk
        # self.chb_risk_kospi_rate
        # self.dspn_risk_kospi_rate
        # self.chb_risk_kosdaq_rate
        # self.dspn_risk_kosdaq_rate
        # self.chb_option_duedate
        # self.spb_option_duedate
        # self.chb_risk_total_loss_price
        # self.spb_risk_total_loss_price
        # self.chb_risk_kospi_loss_count
        # self.spn_risk_kospi_loss_count
        # self.chb_risk_kosdaq_loss_count
        # self.spb_risk_kosdaq_loss_count
    def set_table_header(self):
        self.account_header = ["총매입", "총평가", "총손익", "수익률", "실현손익", "추정자산"]
        self.main_ui.tbl_total_trade_result.setRowCount(1)
        self.main_ui.tbl_total_trade_result.setColumnCount(len(self.account_header))
        self.main_ui.tbl_total_trade_result.setHorizontalHeaderLabels(self.account_header)
        for col, h in enumerate(self.account_header):
            self.main_ui.tbl_total_trade_result.setItem(0, col, QTableWidgetItem(""))

        header = ["계좌번호", "현재잔액", "누적수익", "투자수익율"]
        self.main_ui.tbl_account_info.setRowCount(1)
        self.main_ui.tbl_account_info.setColumnCount(len(header))
        self.main_ui.tbl_account_info.setHorizontalHeaderLabels(header)
        for col, h in enumerate(header):
            self.main_ui.tbl_account_info.setItem(0, col, QTableWidgetItem("1"))

        header = ["계좌번호", "현재잔액", "누적수익", "투자수익율"]
        self.main_ui.tbl_trade_history.setRowCount(1)
        self.main_ui.tbl_trade_history.setColumnCount(len(header))
        self.main_ui.tbl_trade_history.setHorizontalHeaderLabels(header)
        for col, h in enumerate(header):
            self.main_ui.tbl_trade_history.setItem(0, col, QTableWidgetItem("1"))

        header = ["계좌번호", "현재잔액", "누적수익", "투자수익율"]
        self.main_ui.tbl_condition_search_history.setRowCount(1)
        self.main_ui.tbl_condition_search_history.setColumnCount(len(header))
        self.main_ui.tbl_condition_search_history.setHorizontalHeaderLabels(header)
        for col, h in enumerate(header):
            self.main_ui.tbl_condition_search_history.setItem(0, col, QTableWidgetItem("1"))

        header = ["계좌번호", "현재잔액", "누적수익", "투자수익율"]
        self.main_ui.tbl_not_conclude_stock.setRowCount(1)
        self.main_ui.tbl_not_conclude_stock.setColumnCount(4)
        self.main_ui.tbl_not_conclude_stock.setHorizontalHeaderLabels(header)
        for col, h in enumerate(header):
            self.main_ui.tbl_not_conclude_stock.setItem(0, col, QTableWidgetItem("1"))
    def init_event(self):
        # strategy
        self.main_ui.cmb_strategy_list.currentIndexChanged.connect(self.reload_strategy)
        self.main_ui.btn_strategy_save.clicked.connect(self.save_strategy)
        self.main_ui.btn_strategy_reset.clicked.connect(self.reload_strategy)
        self.main_ui.btn_strategy_delete.clicked.connect(self.delete_strategy)

        # buy method
        self.main_ui.cmb_buy_method_list.currentIndexChanged.connect(self.reload_buy_method)
        self.main_ui.btn_buy_method_save.clicked.connect(self.save_buy_method)
        self.main_ui.btn_buy_method_reset.clicked.connect(self.reload_buy_method)
        self.main_ui.btn_buy_method_delete.clicked.connect(self.delete_buy_method)

        # sell method
        self.main_ui.cmb_sell_method_list.currentIndexChanged.connect(self.reload_sell_method)
        self.main_ui.btn_sell_method_save.clicked.connect(self.save_sell_method)
        self.main_ui.btn_sell_method_reset.clicked.connect(self.reload_sell_method)
        self.main_ui.btn_sell_method_delete.clicked.connect(self.delete_sell_method)

        # menu
        self.main_ui.menu_login.triggered.connect(self.menu_login)
        self.main_ui.menu_exit.triggered.connect(self.menu_exit)
        self.main_ui.menu_collect_data.triggered.connect(self.menu_collect_data)
        self.main_ui.menu_trade_report.triggered.connect(self.menu_trade_report)
        self.main_ui.menu_analyze_report.triggered.connect(self.menu_analyze_report)
        self.main_ui.menu_doc.triggered.connect(self.menu_doc)
        self.main_ui.menu_contact.triggered.connect(self.menu_contact)

        # test
        self.main_ui.btn_test_01.clicked.connect(self.test_01)
        self.main_ui.btn_test_02.clicked.connect(self.test_02)
        self.main_ui.btn_test_03.clicked.connect(self.test_03)
        self.main_ui.btn_test_04.clicked.connect(self.test_04)
        self.main_ui.btn_test_05.clicked.connect(self.test_05)
        self.main_ui.btn_test_06.clicked.connect(self.test_06)
        self.main_ui.btn_test_07.clicked.connect(self.test_07)
        self.main_ui.btn_test_08.clicked.connect(self.test_08)

    def connect_trader(self, trader):
        # auto trading
        self.main_ui.rdbtn_auto_buy_start.clicked.connect(self.main_ui.trader.buyer.monitoring)
        self.main_ui.trader.buyer.buy_signal.connect(self.main_ui.buy)
        self.main_ui.rdbtn_auto_buy_stop.clicked.connect(self.main_ui.stop_buying)
        self.main_ui.rdbtn_auto_sell_start.clicked.connect(self.main_ui.trader.seller.monitoring)
        self.main_ui.trader.seller.sell_signal.connect(self.main_ui.sell)
        self.main_ui.rdbtn_auto_sell_stop.clicked.connect(self.main_ui.stop_selling)

        self.main_ui.rdbtn_simul_start.clicked.connect(self.main_ui.trader.simulator.condition_search)
        self.main_ui.trader.simulator.simulation_signal.connect(self.main_ui.hit_stock)
        self.main_ui.rdbtn_simul_stop.clicked.connect(self.main_ui.stop_simulation)

    # Define Menu Interaction___________________S
    # 1. Settings
    def refresh_strategy_list(self, curr_strategy, strategy_list):
        self.refresh_strategy_flag = True
        self.main_ui.cmb_strategy_list.clear()
        strategy_list = util.move_to_first(strategy_list, curr_strategy)
        for strategy in strategy_list:
            self.main_ui.cmb_strategy_list.addItem(strategy)
        self.refresh_strategy_flag = False

    def load_strategy(self, curr_strategy=None):
        # load config
        strategy_conf = config_mgr.load_config('strategy')
        strategy_list = list(strategy_conf.keys())

        # set current strategy
        if curr_strategy is None:
            curr_strategy = strategy_list[0]

        # refresh UI
        self.refresh_strategy_list(curr_strategy, strategy_list)

        # set setting value of strategy
        curr_strategy_conf = strategy_conf[curr_strategy]
        for strategy_group in self.strategy_groups:
            for k, widget, w_type in strategy_group:
                self.set_widget(widget, w_type, curr_strategy_conf[k])
    def reload_strategy(self, curr_strategy=None):
        # handle clear()
        if self.refresh_strategy_flag:
            return
        try:
            if str(curr_strategy).isdigit():
                self.delete_reload = True
            # click reset button(curr_strategy == False) or changed value in combobox(curr_strategy == number)
            if curr_strategy == False or str(curr_strategy).isdigit():
                #print(self.main_ui.cmb_buy_method_list.itemData(ret))
                self.load_strategy(self.main_ui.cmb_strategy_list.currentText())
            else:
                self.load_strategy(curr_strategy)

            self.delete_reload = False
        except Exception:
            # save new value in combobox and refresh combobox
            self.load_strategy(curr_strategy)
    def save_strategy(self):
        print("save_strategy")
        strategy_conf = config_mgr.load_config('strategy')
        strategy_name = self.main_ui.le_strategy.text()
        if strategy_name == "":
            strategy_name = self.main_ui.cmb_strategy_list.currentText()

        if strategy_name not in strategy_conf.keys():
            strategy_conf[strategy_name] = {}

        for strategy_group in self.strategy_groups:
            for k, widget, w_type in strategy_group:
                strategy_conf[strategy_name][k] = self.get_widget(widget, w_type)

        config_mgr.save_config('strategy', strategy_conf)

        # pdb.set_trace()
        curr_strategy = self.main_ui.le_strategy.text()
        if curr_strategy == "":
            curr_strategy = self.main_ui.cmb_strategy_list.currentText()
        self.reload_strategy(curr_strategy)
    def delete_strategy(self):
        print("delete_strategy")
        strategy_conf = config_mgr.load_config('strategy')
        strategy_name = self.main_ui.cmb_strategy_list.currentText()
        strategy_index = self.main_ui.cmb_strategy_list.currentIndex()

        # check if a item is the last one
        if self.main_ui.cmb_strategy_list.count() == 1:
            print("[Error] Don't remove the last item.")
            return

        # save config to config file
        del strategy_conf[strategy_name]
        config_mgr.save_config('strategy', strategy_conf)

        # get new strategy
        curr_strategy = list(strategy_conf.keys())[0]

        # refresh
        self.reload_strategy(curr_strategy)
    def refresh_buy_method_list(self, curr_buy_method, buy_method_list):
        self.refresh_buy_method_flag = True
        self.main_ui.cmb_buy_method_list.clear()
        buy_method_list = util.move_to_first(buy_method_list, curr_buy_method)
        for buy_method in buy_method_list:
            self.main_ui.cmb_buy_method_list.addItem(buy_method)
        self.refresh_buy_method_flag = False
    def load_buy_method(self, curr_buy_method=None):
        # load config
        buy_method_conf = config_mgr.load_config('buy_method')
        buy_method_list = list(buy_method_conf.keys())

        # set current buy_method
        if curr_buy_method is None:
            curr_buy_method = buy_method_list[0]

        # refresh UI
        self.refresh_buy_method_list(curr_buy_method, buy_method_list)

        # set setting value of buy method
        curr_buy_method_conf = buy_method_conf[curr_buy_method]
        for buy_method_group in self.buy_method_groups:
            for k, widget, w_type in buy_method_group:
                self.set_widget(widget, w_type, curr_buy_method_conf[k])

        # set buy method to strategy area
        if self.first_buy_call:
            for buy_method_widget in self.cmb_buy_method_group:
                for item in buy_method_list:
                    buy_method_widget[1].addItem(item)
            self.first_buy_call = False
    def reload_buy_method(self, curr_buy_method=None):
        # handle clear()
        if self.refresh_buy_method_flag:
            return
        try:
            # click reset button(curr_buy_method == False) or changed value in combobox(curr_buy_method == number)
            if curr_buy_method == False or str(curr_buy_method).isdigit():
                # print(self.main_ui.cmb_buy_method_list.itemData(ret))
                self.load_buy_method(self.main_ui.cmb_buy_method_list.currentText())
            else:
                self.load_buy_method(curr_buy_method)
        except Exception:
            # save new value in combobox and refresh combobox
            self.load_buy_method(curr_buy_method)
    def save_buy_method(self):
        new_item_flag = False
        # load config
        buy_method_conf = config_mgr.load_config('buy_method')
        buy_method_name = self.main_ui.le_buy_method.text()
        if buy_method_name == "":
            buy_method_name = self.main_ui.cmb_buy_method_list.currentText()

        if buy_method_name not in buy_method_conf.keys():
            new_item_flag = True
            buy_method_conf[buy_method_name] = {}

        # get setting value of buy method for saveing config
        for buy_method_group in self.buy_method_groups:
            for k, widget, w_type in buy_method_group:
                buy_method_conf[buy_method_name][k] = self.get_widget(widget, w_type)

        # save config
        config_mgr.save_config('buy_method', buy_method_conf)

        # reload buy method if new buy method is stored
        if new_item_flag:
            self.reload_buy_method(self.main_ui.le_buy_method.text())

            for buy_method_widget in self.cmb_buy_method_group:
                self.add_combobox_item(buy_method_widget[1], buy_method_name)
                # buy_method_widget[1].addItem(buy_method_name)
    def delete_buy_method(self):
        self.delete_reload = True
        buy_method_conf = config_mgr.load_config('buy_method')
        buy_method_name = self.main_ui.cmb_buy_method_list.currentText()
        buy_method_index = self.main_ui.cmb_buy_method_list.currentIndex()

        # check if a item is the last one
        if self.main_ui.cmb_buy_method_list.count() == 1:
            print("[Error] Don't remove the last item.")
            return

        # save config to config file
        del buy_method_conf[buy_method_name]
        config_mgr.save_config('buy_method', buy_method_conf)

        # get new buy_method
        curr_buy_method = list(buy_method_conf.keys())[0]

        # refresh buy_method area
        self.reload_buy_method(curr_buy_method)

        # sync to strategy area
        for buy_method_widget in self.cmb_buy_method_group:
            self.remove_combobox_item(buy_method_widget[1], buy_method_name)
        self.delete_reload = False
    def refresh_sell_method_list(self, curr_sell_method, sell_method_list):
        self.refresh_sell_method_flag = True
        self.main_ui.cmb_sell_method_list.clear()
        sell_method_list = util.move_to_first(sell_method_list, curr_sell_method)
        for sell_method in sell_method_list:
            self.main_ui.cmb_sell_method_list.addItem(sell_method)
        self.refresh_sell_method_flag = False
    def load_sell_method(self, curr_sell_method=None):
        # load config
        sell_method_conf = config_mgr.load_config('sell_method')
        sell_method_list = list(sell_method_conf.keys())

        # set current sell_method
        if curr_sell_method is None:
            curr_sell_method = sell_method_list[0]

        # refresh UI
        self.refresh_sell_method_list(curr_sell_method, sell_method_list)

        # set setting value of sell method
        curr_sell_method_conf = sell_method_conf[curr_sell_method]
        for sell_method_group in self.sell_method_groups:
            for k, widget, w_type in sell_method_group:
                self.set_widget(widget, w_type, curr_sell_method_conf[k])

        # set sell method to strategy area
        if self.first_sell_call:
            for sell_method_widget in self.cmb_sell_method_group:
                for item in sell_method_list:
                    sell_method_widget[1].addItem(item)
            self.first_sell_call = False
    def reload_sell_method(self, curr_sell_method=None):
        # handle clear()
        if self.refresh_sell_method_flag:
            return
        try:
            # click reset button(curr_sell_method == False) or changed value in combobox(curr_sell_method == number)
            if curr_sell_method == False or str(curr_sell_method).isdigit():
                # print(self.main_ui.cmb_sell_method_list.itemData(ret))
                self.load_sell_method(self.main_ui.cmb_sell_method_list.currentText())
            else:
                self.load_sell_method(curr_sell_method)
        except Exception:
            # save new value in combobox and refresh combobox
            self.load_sell_method(curr_sell_method)
    def save_sell_method(self):
        new_item_flag = False
        # load config
        sell_method_conf = config_mgr.load_config('sell_method')
        sell_method_name = self.main_ui.le_sell_method.text()
        if sell_method_name == "":
            sell_method_name = self.main_ui.cmb_sell_method_list.currentText()

        if sell_method_name not in sell_method_conf.keys():
            new_item_flag = True
            sell_method_conf[sell_method_name] = {}

        # get setting value of sell method for saveing config
        for sell_method_group in self.sell_method_groups:
            for k, widget, w_type in sell_method_group:
                sell_method_conf[sell_method_name][k] = self.get_widget(widget, w_type)

        # save config
        config_mgr.save_config('sell_method', sell_method_conf)

        # reload sell method if new sell method is stored
        if new_item_flag:
            self.reload_sell_method(self.main_ui.le_sell_method.text())

            for sell_method_widget in self.cmb_sell_method_group:
                self.add_combobox_item(sell_method_widget[1], sell_method_name)
                # sell_method_widget[1].addItem(sell_method_name)
    def delete_sell_method(self):
        self.delete_reload = True
        sell_method_conf = config_mgr.load_config('sell_method')
        sell_method_name = self.main_ui.cmb_sell_method_list.currentText()
        sell_method_index = self.main_ui.cmb_sell_method_list.currentIndex()

        # check if a item is the last one
        if self.main_ui.cmb_sell_method_list.count() == 1:
            print("[Error] Don't remove the last item.")
            return

        # save config to config file
        del sell_method_conf[sell_method_name]
        config_mgr.save_config('sell_method', sell_method_conf)

        # get new sell_method
        curr_sell_method = list(sell_method_conf.keys())[0]

        # refresh sell_method area
        self.reload_sell_method(curr_sell_method)

        # sync to strategy area
        for sell_method_widget in self.cmb_sell_method_group:
            self.remove_combobox_item(sell_method_widget[1], sell_method_name)
        self.delete_reload = False

    # 2. Menu
    def menu_login(self):
        self.kw.login()
    def menu_exit(self):
        print("Program Exit")
        exit(0)
    def menu_collect_data(self):
        """
        [시나리오]
        menu_collect_data 버튼을 누르면, 수집할 data 의 종류와 현재 수집된 data의 상태가 보인다.
        그리고 start 버튼을 누르면 백그라운드에서 data를 수집하고, statusbar 또는 progressbar 를 통해 진행상황을 알려준다.

        [수집할 데이터의 종류]
        kospi/kosdaq 의 주가와 거래량 (1분봉, 3분봉, 5분봉, 10분봉, 30분봉, 일봉, 주봉, 월봉) 데이터
        각 차트종류에 따른 보조지표 (MACD, RSI, 이격도, 이평선 등등) 데이터
        ? 조건식 검출된 종목 데이터(검출시간, 종목명, 종목코드, 검출되었을때의 주가, 체결강도, 등등)
        :return:
        """

        단타종목 = []
        # rqname, 시장구분, 등락구분, 시간구분, 시간, 거래량구분, 종목조건, 신용조건, 가격조건, 상하한포함):
        급등락정보 = self.kw.tr_가격급등락요청("가격급등락요청", "000", "1", "2", "1", "00100", "1", "0", "0", "1")
        급등종목코드 = list(급등락정보.keys())

        단타종목 = 급등종목코드
        단타종목 += self.dbm.load_today_조건검색식종목()

        # 틱 차트 데이터 수집
        # for code in 단타종목:
        단타종목갯수 = len(단타종목)
        for i, code in enumerate(단타종목[:3]):
            print("{}/{}".format(i, 단타종목갯수))
            self.dbm.save_stock_data_tick("1틱봉", code)
            self.dbm.save_stock_data_tick("3틱봉", code)
            self.dbm.save_stock_data_tick("5틱봉", code)
            self.dbm.save_stock_data_tick("10틱봉", code)
            self.dbm.save_stock_data_tick("30틱봉", code)

            # 분봉 데이터 수집
            self.dbm.save_stock_data_min("1분봉", code)
            self.dbm.save_stock_data_min("3분봉", code)
            self.dbm.save_stock_data_min("5분봉", code)
            self.dbm.save_stock_data_min("10분봉", code)
            self.dbm.save_stock_data_min("30분봉", code)

            # 일봉 데이터 수집
            self.dbm.save_stock_data_day("일봉", code, "20180121")
            # 주봉 데이터 수집
            self.dbm.save_stock_data_week("주봉", code, "20180101", "20180121")
            # 월봉 데이터 수집
            self.dbm.save_stock_data_month("월봉", code, "20180101", "20180121")

    def menu_trade_report(self):
        pass
    def menu_analyze_report(self):
        pass
    def menu_doc(self):
        pass
    def menu_contact(self):
        pass

    # 3. Order
    def order(self):
        order_type = self.main_ui.cmb_order_type_gubun.currentText()
        code = self.main_ui.le_order_code.text()
        quantity = self.main_ui.spb_order_quantity.value()
        price = self.main_ui.spb_order_price.value()
        hoga_gubun = self.main_ui.cmb_order_hoga_gubun.currentText()
        orig_order_no = self.main_ui.le_orig_order_num.text()

        self.kw.order(order_type, code, quantity, price, hoga_gubun, orig_order_no)

    # 4. Risk
    def set_risk_stocks(self): # 거래 제외종목 설정
        pass
    def emergency_order(self): # 전량 시장가 매도
        pass
    # Define Menu Interaction___________________E

    # KiWoom Callback_________________________S
    def enable_widget_after_login(self):
        self.main_ui.rdbtn_auto_buy_start.setEnabled(True)
        self.main_ui.rdbtn_auto_buy_stop.setEnabled(True)
        self.main_ui.rdbtn_auto_sell_start.setEnabled(True)
        self.main_ui.rdbtn_auto_sell_stop.setEnabled(True)
        self.main_ui.rdbtn_simul_start.setEnabled(True)
        self.main_ui.rdbtn_simul_stop.setEnabled(True)

    def login_callback(self, **args):
        err_code = args['err_code']
        if err_code == 0:
            self.status_bar.showMessage("connected")

            # 계좌정보
            # 모의투자/실투자에 따른 mini주문 화면 설정
            # 조건식 loading
            # 실시간 업데이트 테이블 UI 업데이트
            self.init_kw_ui()
            # self.slack.chat.post_message("#general", "Login Success")
        else:
            self.status_bar.showMessage("disconnected")
            # self.slack.chat.post_message("#general", "Login Failed")

    def rec_real_data_callback(self, **args):
        data = args['data']

    def init_kw_ui(self):
        # market_info = self.kw.stock_info
        # condition = self.kw.condition
        # server_gubun = self.server_gubun
        # account_info = self.account_info
        print("kiwoom ui update")
        self.enable_widget_after_login()


        # set mini order area
        self.main_ui.cmb_order_hoga_gubun.addItems(OrderType.ORDER_TYPE.keys())
        self.main_ui.cmb_order_type_gubun.addItems(TradeGubun.거래구분[self.kw.server_gubun].keys())

        # set condition
        for cmb in self.buy_cmb_condition_group:
            cmb[1].addItems(self.kw.condition.keys())

        # set theme
        for cmb in self.buy_cmb_theme_group:
            cmb[1].addItems([name for code, name in self.kw.theme])

        # set account list
        self.main_ui.cmb_account_no.addItems(self.kw.account_info["account_list"])
        curr_account = self.kw.account_info["curr_account"]
        self.main_ui.cmb_account_no.setCurrentText(curr_account)

        pdb.set_trace()
        # self.kw.tr_계좌수익률요청("계좌수익률요청", curr_account)
        # time.sleep(0.2)

        # self.kw.tr_계좌평가현황요청("계좌평가현황요청", curr_account)
        # time.sleep(0.2)

        # self.kw.tr_체결잔고요청("체결잔고요청", curr_account)
        # time.sleep(0.2)

        code = "009320" # 대우부품
        s_date = "20180108"
        e_date = "20180117"
        self.kw.tr_일자별종목별실현손익("일자별종목별실현손익", curr_account, code, s_date)


    def update_account_table(self):
        self.main_ui.tbl_total_trade_result.clear()
        self.main_ui.tbl_total_trade_result.setRowCount(1)
        self.main_ui.tbl_total_trade_result.setColumnCount(len(self.account_header))
        self.main_ui.tbl_total_trade_result.setHorizontalHeaderLabels(self.account_header)

        # self.kw.account_table_info
        for col, h in enumerate(self.account_header):
            print(self.kw.account_table_info[h])
            item = QTableWidgetItem(self.kw.account_table_info[h])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.main_ui.tbl_total_trade_result.setItem(0, col, item)
    # KiWoom Callback_________________________S


    # Data structure____________________S
    def set_widget(self, w, w_type, val):
        if w_type == "checkbox":
            w.setChecked(val)
        elif w_type == "timeedit":
            h, m, s = map(lambda x: int(x), val.split(":"))
            w.setTime(QTime(h, m, s))
        elif w_type == "combobox":
            if self.delete_reload:
                if val == "":
                    w.setCurrentText("*" + val)
                    return

                all_item = [txt for index, txt in self.get_all_combobox_item(w)]
                # pdb.set_trace()
                if val not in all_item:
                    if "*"+val not in all_item:
                        # pdb.set_trace()
                        w.addItem("*"+val)
                    w.setCurrentText("*"+val)
                else:
                    w.setCurrentText(val)
            else:
                w.setCurrentText(val)
        elif w_type == "spinbox":
            w.setValue(val)
        elif w_type == "doublespinbox":
            w.setValue(val)
    def get_widget(self, w, w_type):
        data = None
        if w_type == "checkbox":
            data = w.isChecked()
        elif w_type == "timeedit":
            data = w.time().toString()  # HH:MM:SS
        elif w_type == "combobox":
            data = w.currentText()
        elif w_type == "spinbox":
            data = w.value()
        elif w_type == "doublespinbox":
            data = w.value()
        return data
    # Data structure____________________E

    # handle widget more comfortable____________________S
    def get_all_combobox_item(self, cmb):
        all_items = [(i, cmb.itemText(i)) for i in range(cmb.count())]
        return all_items
    def remove_combobox_item(self, cmb, item):
        curr_item = cmb.currentText()
        for i, txt in self.get_all_combobox_item(cmb):
            if item == txt:
                cmb.removeItem(i)

                if curr_item == txt:
                    cmb.addItem("*" + curr_item)
                    cmb.setCurrentText("*" + curr_item)
    def add_combobox_item(self, cmb, item):
        cmb.addItem(item)
        curr_item = cmb.currentText()
        for i, txt in self.get_all_combobox_item(cmb):
            if txt.startswith("*") and txt[1:] == item:
                cmb.removeItem(i)

                if curr_item == txt:
                    cmb.setCurrentText(item)
    # handle widget more comfortable____________________S
    def get_checked_condition_name_list(self):
        condi_list = []
        for i, chk in enumerate(self.buy_chb_condition_group):
            if chk[1].isChecked():
                condi_list.append(self.buy_cmb_condition_group[i][1].currentText())
        return condi_list

    def test_01(self):
        # 비덴트
        data = self.kw.tr_collect_stock_data_min('1분봉', '121800')
        # data[0] = {'현재가': '+18250', '거래량': '70664', '체결시간': '20180119153000', '시가': '+18250', '고가': '+18250', '저가': '+18250', '수정주가구분': '', '수정비욜': '', '대업종구분': '', '소업종구분': '', '종목정보': '', '수정주가이벤트': '', '전일종가': ''}
        print('test_01')
        self.dbm.save_data_to_db(data, '1분봉', '121800', '체결시간')

    def test_02(self):
        data = self.kw.tr_collect_stock_data_day('일봉', '121800', "20180121")
        self.dbm.save_data_to_db(data, '일봉', '121800', '일자')
    def test_03(self):
        pass
    def test_04(self):
        pass
    def test_05(self):
        pass
    def test_06(self):
        pass
    def test_07(self):
        pass
    def test_08(self):
        pass