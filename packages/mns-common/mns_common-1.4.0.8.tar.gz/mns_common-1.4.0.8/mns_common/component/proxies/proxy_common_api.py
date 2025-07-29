import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

import mns_common.api.proxies.liu_guan_proxy_api as liu_guan_proxy_api
import pandas as pd
import mns_common.utils.data_frame_util as data_frame_util
from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.constant.db_name_constant as db_name_constant
import datetime
import requests
import time
from loguru import logger
from functools import lru_cache
import mns_common.api.em.real_time.east_money_stock_a_api as east_money_stock_a_api
import threading

mongodb_util = MongodbUtil('27017')


def query_liu_guan_proxy_ip():
    ip_proxy_pool = mongodb_util.find_all_data(db_name_constant.IP_PROXY_POOL)
    return ip_proxy_pool


def remove_proxy_ip():
    mongodb_util.remove_data({}, db_name_constant.IP_PROXY_POOL)


def check_valid(ip_proxy_pool):
    effect_time = list(ip_proxy_pool['effect_time'])[0]

    now_date = datetime.datetime.now()

    str_now_date = now_date.strftime('%Y-%m-%d %H:%M:%S')

    if effect_time > str_now_date:
        return True
    else:
        remove_proxy_ip()
        return False


@lru_cache(maxsize=None)
def get_account_cache():
    query = {"type": "liu_guan_proxy", }
    return mongodb_util.find_query_data(db_name_constant.STOCK_ACCOUNT_INFO, query)


def generate_proxy_ip_api(minutes):
    stock_account_info = get_account_cache()
    order_id = list(stock_account_info['password'])[0]
    secret = list(stock_account_info['account'])[0]
    # 获取10分钟动态ip
    ip = liu_guan_proxy_api.get_proxy_api(order_id, secret, str(60 * minutes))
    return ip


def generate_proxy_ip(minutes):
    ip_proxy_pool = mongodb_util.find_all_data(db_name_constant.IP_PROXY_POOL)
    if data_frame_util.is_not_empty(ip_proxy_pool):
        return list(ip_proxy_pool['ip'])[0]
    else:
        remove_proxy_ip()
        now_date = datetime.datetime.now()
        # 加上分钟
        time_to_add = datetime.timedelta(minutes=minutes)
        new_date = now_date + time_to_add
        str_now_date = new_date.strftime('%Y-%m-%d %H:%M:%S')
        # 获取10分钟动态ip
        while True:
            remove_proxy_ip()
            ip = generate_proxy_ip_api(minutes)
            if check_proxy(ip):
                result_dict = {"_id": ip,
                               'effect_time': str_now_date,
                               'ip': ip}
                result_df = pd.DataFrame(result_dict, index=[1])

                mongodb_util.insert_mongo(result_df, db_name_constant.IP_PROXY_POOL)
                break
            else:
                time.sleep(0.5)
        return ip


def get_proxy_ip(minutes):
    ip_proxy_pool = query_liu_guan_proxy_ip()
    if data_frame_util.is_empty(ip_proxy_pool):
        return generate_proxy_ip(minutes)
    else:
        if check_valid(ip_proxy_pool):
            return list(ip_proxy_pool['ip'])[0]
        else:
            return generate_proxy_ip(minutes)


def check_proxy(proxy_ip):
    try:
        # 两秒超时
        test_df = call_with_timeout(get_em_real_time_data, proxy_ip, timeout=2)
        if data_frame_util.is_not_empty(test_df):
            logger.info("可用代理ip:{}", proxy_ip)
            return True
        else:
            return False
    except Exception as e:
        logger.error("代理ip不可用:{},{}", proxy_ip, e)
        return False


def get_em_real_time_data(proxy_ip):
    proxies = {
        "http": proxy_ip,
        "https": proxy_ip
    }
    return east_money_stock_a_api.get_stock_page_data(1, proxies, 20)


# 定义一个带超时的函数调用
def call_with_timeout(func, *args, timeout=2, **kwargs):
    # 用于存储函数执行结果
    result = None
    exception = None

    # 定义一个线程目标函数
    def target():
        nonlocal result, exception
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            exception = e

    # 创建线程并启动
    thread = threading.Thread(target=target)
    thread.start()

    # 等待线程完成，最多等待 timeout 秒
    thread.join(timeout)

    # 如果线程仍然存活，说明函数超时了
    if thread.is_alive():
        raise TimeoutError(f"Function exceeded timeout of {timeout} seconds")

    # 如果函数抛出了异常，重新抛出
    if exception is not None:
        raise exception
    return result


if __name__ == "__main__":
    generate_proxy_ip(1)
