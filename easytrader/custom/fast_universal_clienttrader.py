# -*- coding: utf-8 -*-

import time
import pywinauto
import pywinauto.clipboard
import functools
from pywinauto.timings import wait_until_passes

from easytrader import grid_strategies, pop_dialog_handler, refresh_strategies
from .. import universal_clienttrader
from easytrader.utils.perf import perf_clock
from easytrader.log import logger
import easyutils

# 自定义加速的同花顺客户端，用了一些魔法
class FastUniversalClientTrader(universal_clienttrader.UniversalClientTrader):
    grid_strategy = grid_strategies.Copy

    @property
    def broker_type(self):
        return "universal"

    @perf_clock
    def _switch_left_menus(self, path, sleep=0.2):
        if ("F1" in path[0] and len(path) == 1):
            return self._switch_left_menus_by_shortcut("{F1}", sleep=0.2)
        elif ("F2" in path[0] and len(path) == 1):
            return self._switch_left_menus_by_shortcut("{F2}", sleep=0.2)
        elif ("F3" in path[0] and len(path) == 1):
            return self._switch_left_menus_by_shortcut("{F3}", sleep=0.2)
        elif ("F4" in path[0] and len(path) == 1):
            return self._switch_left_menus_by_shortcut("{F4}", sleep=0.2)
        else:
            return super()._switch_left_menus(path, sleep)

    @property
    def position(self):
        # 因为 资金股票 是 F4 的第一项，所以可以用快捷键
        # self._switch_left_menus(["查询[F4]", "资金股票"])
        self._switch_left_menus(["查询[F4]"])

        return self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID)

    @perf_clock
    def buy_with_default_price(self, security, amount):
        # 两次操作可以聚焦到首个输入框
        self._switch_left_menus(["卖出[F2]"])
        self._switch_left_menus(["买入[F1]"])

        return self._trade_with_default_price(security, amount)

    @perf_clock
    def sell_with_default_price(self, security, amount):
        # 两次操作可以聚焦到首个输入框
        self._switch_left_menus(["买入[F1]"])
        self._switch_left_menus(["卖出[F2]"])

        return self._trade_with_default_price(security, amount)

    @perf_clock
    def buy(self, security, price, amount):
        # 两次操作可以聚焦到首个输入框
        # 不过稳定性需要优化，偶现在卖出界面买入的情况
        self._switch_left_menus(["卖出[F2]"])
        self._switch_left_menus(["买入[F1]"])

        return self.trade(security, price, amount)

    @perf_clock
    def sell(self, security, price, amount):
        # 两次操作可以聚焦到首个输入框
        self._switch_left_menus(["买入[F1]"])
        self._switch_left_menus(["卖出[F2]"])

        return self.trade(security, price, amount)

    def _trade_with_default_price(self, security, amount):
        self._set_with_default_price_and_submit(security, amount)

        self._submit_trade()

        return self._handle_pop_dialogs(
            handler_class=pop_dialog_handler.TradePopDialogHandler
        )

    @perf_clock
    def _set_with_default_price_and_submit(self, security, amount):
        code = security[-6:]
        quantity = str(int(amount))

        # # 价格是默认的，切换到数量
        # 2. 输入证券代码，按 Tab 切换到价格
        self._main.type_keys(f"{{BACKSPACE 6}}{{PAUSE 0.1}}"
                             f"{code}{{TAB}}{{TAB}}{quantity}{{TAB}}"
                             f"{{PAUSE 0.1}}{{ENTER}}")

    @perf_clock
    def _set_trade_params(self, security, price, amount):
        code = security[-6:]
        rounded_price = easyutils.round_price_by_code(price, code)
        quantity = str(int(amount))

        # 1. 按 Tab 聚焦到第一个输入框
        # self._main.type_keys("{TAB}")

        # 2. 输入证券代码，按 Tab 切换到交易所
        self._main.type_keys(f"{{BACKSPACE 6}}{{PAUSE 0.1}}"
                             f"{code}{{TAB}}{{PAUSE 0.1}}"
                             f"{{BACKSPACE 9}}{{PAUSE 0.1}}"
                             f"{rounded_price}{{TAB}}{quantity}{{TAB}}"
                             f"{{PAUSE 0.1}}{{ENTER}}")


    @functools.lru_cache()
    def _get_main_child_window(self, control_id, class_name):
        return self._main.child_window(control_id=control_id, class_name="Edit")


    @perf_clock
    def _submit_trade(self):
        # time.sleep(0.2)
        # time.sleep(0.1)
        # self._app.top_window().type_keys("{ENTER}")
        pass
