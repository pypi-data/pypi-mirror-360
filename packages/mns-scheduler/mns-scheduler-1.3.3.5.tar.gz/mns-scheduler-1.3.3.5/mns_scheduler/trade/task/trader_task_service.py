import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 17
project_path = file_path[0:end]
sys.path.append(project_path)
import mns_common.utils.cmd_util as cmd_util
import time
import mns_scheduler.trade.auto_login.trader_auto_service as trader_auto_service
import mns_common.utils.data_frame_util as data_frame_util
from loguru import logger

# 交易任务
TRADER_SERVER_PATH = 'H:\\mns-trader.bat'
# 实时行情同步任务 python名称
TRADER_SERVER_NAME = "mns-trader"


# 打开交易客户端
def open_trader_terminal():
    # 打开任务进程
    cmd_util.open_bat_file(TRADER_SERVER_PATH)
    # 自动登陆
    trader_auto_service.auto_login()
    time.sleep(5)
    # 需先打开同花顺终端在开始交易服务
    kill_server()
    time.sleep(5)
    # 打开任务进程
    cmd_util.open_bat_file(TRADER_SERVER_PATH)


def kill_server():
    all_cmd_processes = cmd_util.get_all_process()
    all_cmd_processes_trader = all_cmd_processes.loc[
        (all_cmd_processes['total_info'].str.contains(TRADER_SERVER_NAME, case=False, na=False))]
    if data_frame_util.is_not_empty(all_cmd_processes_trader):
        for processes_one in all_cmd_processes_trader.itertuples():
            try:
                process_pid = processes_one.process_pid
                cmd_util.kill_process_by_pid(process_pid)
            except BaseException as e:
                logger.error("杀死进程异常:{}", e)


if __name__ == '__main__':
    open_trader_terminal()
