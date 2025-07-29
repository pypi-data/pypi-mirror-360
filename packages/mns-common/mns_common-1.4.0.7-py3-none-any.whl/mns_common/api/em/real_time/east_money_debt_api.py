import sys
import os

import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 14
project_path = file_path[0:end]
sys.path.append(project_path)
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from loguru import logger
import json
import requests
import time
import akshare as ak
import numpy as np

# 最大返回条数
max_number = 600
# 最小返回条数
min_number = 500
# 分页条数
page_number = 100


# fields_02 = "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100,f101,f102,f103,f104,f105,f106,f107,f108" \
#             ",f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200" \
#             ",f209,f210,f211,f212,f213,f214,f215,f216,f217,f218,f219,f220,f221,f222,f223,f224,f225,f226,f227,f228,f229,f230,f231,f232,f233,f234,f235,f236,f237,f238,f239,f240,f241,f242,f243,f244,f245,f246,f247,f248,f249,f250,f251,f252,f253,f254,f255,f256,f257,f258,f259,f260,f261,f262,f263,f264,f265,f266,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f277,f278,f279,f280,f281,f282,f283,f284,f285,f286,f287,f288,f289,f290,f291,f292,f293,f294,f295,f296,f297,f298,f299,f300" \
#             ",f309,f310,f312,f313,f314,f315,f316,f317,f318,f319,f320,f321,f322,f323,f324,f325,f326,f327,f328,f329,f330,f331,f332,f333,f334,f335,f336,f337,f338,f339,f340,f341,f342,f343,f344,f345,f346,f347,f348,f349,f350,f351,f352,f353,f354,f355,f356,f357,f358,f359,f360,f361,f362,f363,f364,f365,f366,f367,f368,f369,f370,f371,f372,f373,f374,f375,f376,f377,f378,f379,f380,f381,f382,f383,f384,f385,f386,f387,f388,f389,f390,f391,f392,f393,f394,f395,f396,f397,f398,f399,f401"
#

#
# url = https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery34103608466964799838_1718163189869&pn=1&np=1&ut
# =8a086bfc3570bdde64a6a1c585cccb35&fltt=1&invt=1&fs=m:0+e:11,m:1+e:11,m:1+e:11+s:4194304,
# m:0+e:11+s:8388608&dpt=zqsc.zpg&fields=f1,f2,f3,f4,f5,f6,f8,f10,f12,f13,f14,f18,f22,f152,
# f237&wbp2u=|0|0|0|wap&fid=f3&po=1&pz=2000&_=1718163189870
def get_debt_page_data(fields, pn, proxies) -> pd.DataFrame:
    current_timestamp = str(int(round(time.time() * 1000, 0)))
    url = "https://push2.eastmoney.com/api/qt/clist/get"

    params = {
        "cb": "jQuery34103608466964799838_" + current_timestamp,
        "pn": str(pn),
        "np": 3,
        "ut": "8a086bfc3570bdde64a6a1c585cccb35",
        "fltt": 1,
        "invt": 1,
        "fs": "m:0+e:11,m:1+e:11,m:1+e:11+s:4194304,m:0+e:11+s:8388608",
        "dpt": "zqsc.zpg",
        "fields": fields,
        "wbp2u": "|0|0|0|wap",
        "fid": "f12",
        "po": 1,
        "pz": 2000,
        "_": current_timestamp
    }
    try:
        if proxies is None:
            r = requests.get(url, params)
        else:
            r = requests.get(url, params, proxies=proxies)
        data_text = r.text

        if pn == 1:
            try:
                begin_index_total = data_text.index('"total":')

                end_index_total = data_text.index('"diff"')
                global max_number
                max_number = int(data_text[begin_index_total + 8:end_index_total - 1])
            except Exception as e:
                logger.error(f"获取第{pn}页可转债列表异常: {e}")
                return pd.DataFrame()

        begin_index = data_text.index('[')
        end_index = data_text.index(']')
        data_json = data_text[begin_index:end_index + 1]
        data_json = json.loads(data_json)
        if data_json is None:
            return pd.DataFrame()
        else:
            return pd.DataFrame(data_json)
    except Exception as e:
        logger.error("获取可转债列表,实时行情异常:{}", e)
        return pd.DataFrame()


def all_debt_ticker_data(fields, proxies) -> pd.DataFrame:
    """
    使用多线程获取所有债券数据
    """
    # 计算总页数，假设总共有1000条数据，每页200条

    per_page = page_number
    total_pages = (max_number + per_page - 1) // per_page  # 向上取整

    # 创建线程池
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务，获取每页数据
        futures = [executor.submit(get_debt_page_data, fields, pn, proxies)
                   for pn in range(1, total_pages + 1)]

        # 收集结果
        results = []
        for future in futures:
            result = future.result()
            if not result.empty:
                results.append(result)

    # 合并所有页面的数据
    if results:
        return pd.concat(results, ignore_index=True)
    else:
        return pd.DataFrame()


def get_debt_real_time_quotes(proxies):
    fields = ("f352,f2,f3,f5,f6,f8,f10,f11,f22,f12,f14,f15,f16,f17,f18,f20,f21,f26,f33,f34,f35,f62,f66,f69,f72,f184,"
              "f211,f212,f232,f233,f234")
    # 获取第一页数据
    page_one_df = get_debt_page_data(fields, 1, proxies)
    # 数据接口正常返回5600以上的数量
    if page_one_df.shape[0] > min_number:
        page_one_df = rename_real_time_quotes_df(page_one_df)
        page_one_df.drop_duplicates('symbol', keep='last', inplace=True)
        return page_one_df
    else:
        page_df = all_debt_ticker_data(fields, proxies)
        page_df = rename_real_time_quotes_df(page_df)
        page_df.drop_duplicates('symbol', keep='last', inplace=True)
        return page_df


def rename_real_time_quotes_df(temp_df):
    temp_df = temp_df.rename(columns={
        "f2": "now_price",
        "f3": "chg",
        "f5": "volume",
        "f6": "amount",
        "f8": "exchange",
        "f10": "quantity_ratio",
        "f22": "up_speed",
        "f11": "up_speed_05",
        "f12": "symbol",
        "f14": "name",
        "f15": "high",
        "f16": "low",
        "f17": "open",
        "f18": "yesterday_price",
        "f20": "total_mv",
        "f21": "flow_mv",
        "f26": "list_date",
        "f33": "wei_bi",
        "f34": "outer_disk",
        "f35": "inner_disk",
        "f62": "today_main_net_inflow",
        "f66": "super_large_order_net_inflow",
        "f69": "super_large_order_net_inflow_ratio",
        "f72": "large_order_net_inflow",
        # "f78": "medium_order_net_inflow",
        # "f84": "small_order_net_inflow",
        # "f103": "concept",
        "f184": "today_main_net_inflow_ratio",
        "f352": "average_price",
        "f211": "buy_1_num",
        "f212": "sell_1_num",
        "f232": "stock_symbol",
        "f234": "stock_name",
        "f233": "market"
    })
    temp_df.loc[temp_df['buy_1_num'] == '-', 'buy_1_num'] = 0
    temp_df.loc[temp_df['sell_1_num'] == '-', 'sell_1_num'] = 0
    temp_df.loc[temp_df['up_speed_05'] == '-', 'up_speed_05'] = 0
    temp_df.loc[temp_df['up_speed'] == '-', 'up_speed'] = 0
    temp_df.loc[temp_df['average_price'] == '-', 'average_price'] = 0
    temp_df.loc[temp_df['wei_bi'] == '-', 'wei_bi'] = 0
    temp_df.loc[temp_df['yesterday_price'] == '-', 'yesterday_price'] = 0
    temp_df.loc[temp_df['now_price'] == '-', 'now_price'] = 0
    temp_df.loc[temp_df['chg'] == '-', 'chg'] = 0
    temp_df.loc[temp_df['volume'] == '-', 'volume'] = 0
    temp_df.loc[temp_df['amount'] == '-', 'amount'] = 0
    temp_df.loc[temp_df['exchange'] == '-', 'exchange'] = 0
    temp_df.loc[temp_df['quantity_ratio'] == '-', 'quantity_ratio'] = 0
    temp_df.loc[temp_df['high'] == '-', 'high'] = 0
    temp_df.loc[temp_df['low'] == '-', 'low'] = 0
    temp_df.loc[temp_df['open'] == '-', 'open'] = 0
    temp_df.loc[temp_df['total_mv'] == '-', 'total_mv'] = 0
    temp_df.loc[temp_df['flow_mv'] == '-', 'flow_mv'] = 0
    temp_df.loc[temp_df['inner_disk'] == '-', 'inner_disk'] = 0
    temp_df.loc[temp_df['outer_disk'] == '-', 'outer_disk'] = 0
    temp_df.loc[temp_df['today_main_net_inflow_ratio'] == '-', 'today_main_net_inflow_ratio'] = 0
    temp_df.loc[temp_df['today_main_net_inflow'] == '-', 'today_main_net_inflow'] = 0
    temp_df.loc[temp_df['super_large_order_net_inflow'] == '-', 'super_large_order_net_inflow'] = 0
    temp_df.loc[temp_df['super_large_order_net_inflow_ratio'] == '-', 'super_large_order_net_inflow_ratio'] = 0
    temp_df.loc[temp_df['large_order_net_inflow'] == '-', 'large_order_net_inflow'] = 0
    temp_df["list_date"] = pd.to_numeric(temp_df["list_date"], errors="coerce")
    temp_df["wei_bi"] = pd.to_numeric(temp_df["wei_bi"], errors="coerce")
    temp_df["average_price"] = pd.to_numeric(temp_df["average_price"], errors="coerce")
    temp_df["yesterday_price"] = pd.to_numeric(temp_df["yesterday_price"], errors="coerce")
    temp_df["now_price"] = pd.to_numeric(temp_df["now_price"], errors="coerce")
    temp_df["chg"] = pd.to_numeric(temp_df["chg"], errors="coerce")
    temp_df["volume"] = pd.to_numeric(temp_df["volume"], errors="coerce")
    temp_df["amount"] = pd.to_numeric(temp_df["amount"], errors="coerce")
    temp_df["exchange"] = pd.to_numeric(temp_df["exchange"], errors="coerce")
    temp_df["quantity_ratio"] = pd.to_numeric(temp_df["quantity_ratio"], errors="coerce")
    temp_df["high"] = pd.to_numeric(temp_df["high"], errors="coerce")
    temp_df["low"] = pd.to_numeric(temp_df["low"], errors="coerce")
    temp_df["open"] = pd.to_numeric(temp_df["open"], errors="coerce")
    temp_df["total_mv"] = pd.to_numeric(temp_df["total_mv"], errors="coerce")
    temp_df["flow_mv"] = pd.to_numeric(temp_df["flow_mv"], errors="coerce")
    temp_df["outer_disk"] = pd.to_numeric(temp_df["outer_disk"], errors="coerce")
    temp_df["inner_disk"] = pd.to_numeric(temp_df["inner_disk"], errors="coerce")
    temp_df["today_main_net_inflow"] = pd.to_numeric(temp_df["today_main_net_inflow"], errors="coerce")
    temp_df["super_large_order_net_inflow"] = pd.to_numeric(temp_df["super_large_order_net_inflow"],
                                                            errors="coerce")
    temp_df["super_large_order_net_inflow_ratio"] = pd.to_numeric(temp_df["super_large_order_net_inflow_ratio"],
                                                                  errors="coerce")
    temp_df["large_order_net_inflow"] = pd.to_numeric(temp_df["large_order_net_inflow"],
                                                      errors="coerce")
    # 大单比例
    temp_df['large_order_net_inflow_ratio'] = round((temp_df['large_order_net_inflow'] / temp_df['amount']) * 100, 2)

    # 外盘是内盘倍数
    temp_df['disk_ratio'] = round((temp_df['outer_disk'] - temp_df['inner_disk']) / temp_df['inner_disk'], 2)
    # 只有外盘没有内盘
    temp_df.loc[temp_df["inner_disk"] == 0, ['disk_ratio']] = 1688

    temp_df['now_price'] = round(temp_df['now_price'] / 1000, 3)
    temp_df['chg'] = round(temp_df['chg'] / 100, 2)
    temp_df['exchange'] = round(temp_df['exchange'] / 100, 2)
    temp_df['quantity_ratio'] = round(temp_df['quantity_ratio'] / 100, 2)

    temp_df['up_speed'] = round(temp_df['up_speed'] / 100, 2)
    temp_df['up_speed_05'] = round(temp_df['up_speed_05'] / 100, 2)

    temp_df['high'] = round(temp_df['high'] / 1000, 2)
    temp_df['low'] = round(temp_df['low'] / 1000, 2)

    temp_df['open'] = round(temp_df['open'] / 1000, 2)
    temp_df['yesterday_price'] = round(temp_df['yesterday_price'] / 1000, 2)
    temp_df['wei_bi'] = round(temp_df['wei_bi'] / 100, 2)
    temp_df['super_large_order_net_inflow_ratio'] = round(temp_df['super_large_order_net_inflow_ratio'] / 100, 2)
    temp_df['today_main_net_inflow_ratio'] = round(temp_df['today_main_net_inflow_ratio'] / 100, 2)
    temp_df['average_price'] = round(temp_df['average_price'] / 1000, 2)

    temp_df.loc[:, 'reference_main_inflow'] = round(
        (temp_df['flow_mv'] * (1 / 1000)), 2)

    temp_df.loc[:, 'main_inflow_multiple'] = round(
        (temp_df['today_main_net_inflow'] / temp_df['reference_main_inflow']), 2)

    temp_df.loc[:, 'super_main_inflow_multiple'] = round(
        (temp_df['super_large_order_net_inflow'] / temp_df['reference_main_inflow']), 2)
    temp_df['large_inflow_multiple'] = round(
        (temp_df['large_order_net_inflow'] / temp_df['reference_main_inflow']), 2)

    # 债权是10
    temp_df['disk_diff_amount'] = round(
        (temp_df['outer_disk'] - temp_df['inner_disk']) * temp_df[
            "average_price"] * 10,
        2)

    temp_df['disk_diff_amount_exchange'] = round(
        (temp_df['disk_diff_amount'] / temp_df['reference_main_inflow']), 2)
    temp_df.loc[:, 'sum_main_inflow_disk'] = temp_df['main_inflow_multiple'] + \
                                             temp_df['disk_diff_amount_exchange']
    temp_df.replace([np.inf, -np.inf], 0, inplace=True)
    temp_df = temp_df.fillna(0)
    return temp_df


# 可转债信息
def get_kzz_bond_info():
    try:
        bond_zh_cov_info_ths_df = ak.bond_zh_cov_info_ths()
        bond_zh_cov_info_ths_df = bond_zh_cov_info_ths_df.rename(columns={
            "债券代码": "symbol",
            "债券简称": "name",
            "申购日期": "apply_date",
            "申购代码": "apply_code",
            "原股东配售码": "config_code",
            "每股获配额": "per_share_limit",
            "计划发行量": "planned_circulation",
            "实际发行量": "actual_circulation",
            "中签公布日": "winning_date",
            "中签号": "winning_number",
            "上市日期": "list_date",
            "正股代码": "stock_code",
            "正股简称": "stock_name",
            "转股价格": "conversion_price",
            "到期时间": "due_date",
            "中签率": "lot_winning_rate"
        })
        return bond_zh_cov_info_ths_df
    except BaseException as e:
        logger.error("获取可转债信息异常:{}", e)


if __name__ == '__main__':
    info_df = get_kzz_bond_info()
    print(info_df)
    while True:
        df = get_debt_real_time_quotes(None)
        logger.info(df)
