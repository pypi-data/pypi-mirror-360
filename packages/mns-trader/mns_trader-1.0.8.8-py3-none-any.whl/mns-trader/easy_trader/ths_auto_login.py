import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

from trader.utils.windows_util import get_all_process
import pywinauto as pw
from loguru import logger

from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.constant.db_name_constant as db_name_constant
from trader.common.terminal_enum import TerminalEnum
mongodb_util = MongodbUtil('27017')


def ths_auto_login():
    query = {'type': TerminalEnum.EASY_TRADER.terminal_code}
    stock_account_info_df = mongodb_util.find_query_data(db_name_constant.STOCK_ACCOUNT_INFO, query)

    connect_path = list(stock_account_info_df['exe_path'])[0]
    all_process_df = get_all_process()
    # 查看下单程序是否已经运行
    is_running = all_process_df.loc[all_process_df['process_name'] == 'xiadan.exe'].shape[0] > 0
    if is_running:
        logger.warning("ths终端已经在运行中")
        return {"result": 'success'}
    else:
        app = pw.Application(backend='uia').start(connect_path, timeout=10)
        app.top_window()

        return {"result": 'success'}


if __name__ == '__main__':
    ths_auto_login()
