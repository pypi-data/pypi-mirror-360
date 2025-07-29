import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

import datetime
import mns_common.utils.date_handle_util as date_util
from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.constant.db_name_constant as db_name_constant
import mns_common.utils.cmd_util as cmd_util
import mns_common.utils.data_frame_util as data_frame_util
import time
from loguru import logger
import mns_common.component.trade_date.trade_date_common_service_api as trade_date_common_service_api

mongodb_util = MongodbUtil('27017')
REAL_TIME_SCHEDULER_NAME = "realtime_quotes_now_sync"
# 实时同步 bat
REAL_TIME_TASK_NAME_PATH = 'H:\\real_time_task.bat'


# 获取同步任务pid
def get_real_time_quotes_task(all_cmd_processes):
    return all_cmd_processes[
        (all_cmd_processes['total_info'].str.contains(REAL_TIME_SCHEDULER_NAME, case=False, na=False))
        | (all_cmd_processes['total_info'].str.contains(REAL_TIME_SCHEDULER_NAME, case=False, na=False))]


# 关闭实时行情任务
def real_time_sync_task_close():
    all_cmd_processes = cmd_util.get_all_process()
    if data_frame_util.is_empty(all_cmd_processes):
        return False
    all_cmd_processes_real_time_task = get_real_time_quotes_task(all_cmd_processes)
    if data_frame_util.is_empty(all_cmd_processes_real_time_task):
        return False
    for match_task_one in all_cmd_processes_real_time_task.itertuples():
        try:
            processes_pid = match_task_one.process_pid
            # 关闭当前进程
            cmd_util.kill_process_by_pid(processes_pid)
        except BaseException as e:
            logger.error("关闭实时行情任务异常:{}", e)


# 重开定时任务同步
def real_time_sync_task_open():
    all_cmd_processes = cmd_util.get_all_process()
    if data_frame_util.is_empty(all_cmd_processes):
        return False
    all_cmd_processes_real_time_task = get_real_time_quotes_task(all_cmd_processes)
    if data_frame_util.is_empty(all_cmd_processes_real_time_task):
        # 重开定时任务
        cmd_util.open_bat_file(REAL_TIME_TASK_NAME_PATH)
        # 防止太快重开多个
        time.sleep(3)


def query_data_exist(str_day):
    col_name = db_name_constant.REAL_TIME_QUOTES_NOW + '_' + str_day
    query = {'symbol': '000001'}
    return mongodb_util.exist_data_query(col_name, query)


def exist_sync_task():
    all_cmd_processes = cmd_util.get_all_process()
    if data_frame_util.is_empty(all_cmd_processes):
        return False
    all_cmd_processes_real_time_task = get_real_time_quotes_task(all_cmd_processes)
    if data_frame_util.is_empty(all_cmd_processes_real_time_task):
        return False
    else:
        return True


def check_data_sync_task_status():
    now_date = datetime.datetime.now()
    if bool(is_data_sync_time(now_date)):
        if bool(1 - exist_sync_task()):
            real_time_sync_task_open()
        time.sleep(1)
    else:
        time.sleep(5)


def is_data_sync_time(now_date):
    # return True
    hour = now_date.hour
    minute = now_date.minute
    second = now_date.second
    str_now_day = now_date.strftime('%Y-%m-%d')
    is_trade_day = trade_date_common_service_api.is_trade_day(str_now_day)
    trade_time = (hour == 9 and minute >= 15) \
                 or (hour == 10) \
                 or (hour == 11 and minute < 30) \
                 or (hour == 11 and minute == 30 and second < 5) \
                 or (hour == 12 and minute == 59) \
                 or (hour == 13) \
                 or (hour == 14) \
                 or (hour == 15 and minute == 0 and second < 10)

    return is_trade_day and trade_time


if __name__ == '__main__':
    # check_data_sync_task_status()
    check_data_sync_task_status()
