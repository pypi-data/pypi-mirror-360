
# 市场概述
from flask import Blueprint
from flask import request
import mns_trader_server.easy_trader.easy_trader_service as easy_trader_service
import mns_trader_server.qmt.qmt_service as qmt_service
from mns_trader_server.common.terminal_enum import TerminalEnum
import mns_trader_server.qmt.qmt_auto_login as qmt_auto_login
import mns_trader_server.easy_trader.ths_auto_login as ths_auto_login

api_blueprint_trader = Blueprint("api_blueprint_trader", __name__)


# 买入
@api_blueprint_trader.route('/buy', methods=['POST'])
def trade_buy():
    symbol = request.json.get("symbol")
    buy_price = request.json.get("buy_price")
    buy_volume = request.json.get("buy_volume")
    terminal = request.json.get("terminal")
    if terminal == TerminalEnum.EASY_TRADER.terminal_code:
        return easy_trader_service.order_buy(symbol, buy_price, buy_volume)
    elif terminal == TerminalEnum.QMT.terminal_code:
        return qmt_service.order_buy(symbol, buy_price, buy_volume)
    else:
        '''
        默认easy_trader
        '''
        return easy_trader_service.order_buy(symbol, buy_price, buy_volume)


# 卖出
@api_blueprint_trader.route('/sell', methods=['POST'])
def trade_sell():
    symbol = request.json.get("symbol")
    sell_price = request.json.get("sell_price")
    sell_volume = request.json.get("sell_volume")
    terminal = request.json.get("terminal")
    if terminal == TerminalEnum.EASY_TRADER.terminal_code:
        return easy_trader_service.order_sell(symbol, sell_price, sell_volume)
    elif terminal == TerminalEnum.QMT.terminal_code:
        return qmt_service.order_sell(symbol, sell_price, sell_volume)
    else:
        '''
        默认easy_trader
        '''
        return easy_trader_service.order_sell(symbol, sell_price, sell_volume)


# 自动一键打新
@api_blueprint_trader.route('/auto/ipo/buy', methods=['POST'])
def auto_ipo_buy():
    terminal = request.json.get("terminal")
    if terminal == TerminalEnum.EASY_TRADER.terminal_code:
        return easy_trader_service.auto_ipo_buy()
    elif terminal == TerminalEnum.QMT.terminal_code:
        return qmt_service.auto_ipo_buy()
    else:
        '''
        默认easy_trader
        '''
        return easy_trader_service.order_buy()


# 获取仓位
@api_blueprint_trader.route('/position', methods=['POST'])
def get_position():
    terminal = request.json.get("terminal")
    if terminal == TerminalEnum.EASY_TRADER.terminal_code:
        return easy_trader_service.get_position()
    elif terminal == TerminalEnum.QMT.terminal_code:
        return qmt_service.get_position()
    else:
        '''
        默认easy_trader
        '''
        return easy_trader_service.get_position()


# 撤单
@api_blueprint_trader.route('/cancel', methods=['POST'])
def order_cancel():
    terminal = request.json.get("terminal")
    entrust_no = request.json.get("entrust_no")
    symbol = request.json.get("symbol")
    if terminal == TerminalEnum.EASY_TRADER.terminal_code:
        return easy_trader_service.order_cancel(entrust_no)
    elif terminal == TerminalEnum.QMT.terminal_code:
        return qmt_service.order_cancel(entrust_no, symbol)
    else:
        '''
        默认easy_trader
        '''
        return easy_trader_service.order_cancel(entrust_no)


# 客户端自动登陆
@api_blueprint_trader.route('/auto/login', methods=['POST'])
def auto_login():
    terminal = request.json.get("terminal")
    if terminal == TerminalEnum.EASY_TRADER.terminal_code:
        return ths_auto_login.ths_auto_login()
    elif terminal == TerminalEnum.QMT.terminal_code:
        return qmt_auto_login.qmt_auto_login()


# 获取账户余额
@api_blueprint_trader.route('/account/balance', methods=['GET'])
def account_balance():
    terminal = request.json.get("terminal")
    if terminal == TerminalEnum.EASY_TRADER.terminal_code:
        return easy_trader_service.get_balance()
    elif terminal == TerminalEnum.QMT.terminal_code:
        return qmt_auto_login.qmt_auto_login()
