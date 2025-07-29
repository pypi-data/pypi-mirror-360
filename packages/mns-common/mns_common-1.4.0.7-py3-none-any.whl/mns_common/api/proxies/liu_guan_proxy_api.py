import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from loguru import logger
import requests
import time
import hashlib
import json

# 提取订单
"""
    orderId:提取订单号
    secret:用户密钥
    num:提取IP个数
    pid:省份
    cid:城市
    type：请求类型，1=http/https,2=socks5
    unbindTime:使用时长，秒/s为单位
    noDuplicate:去重，0=不去重，1=去重
    lineSeparator:分隔符
    singleIp:切换,0=切换，1=不切换
"""


def get_proxy_api(order_id, secret, unbind_time):
    num = "1"
    pid = "-1"
    cid = ""
    noDuplicate = "1"
    lineSeparator = "0"
    singleIp = "0"
    time_str = str(int(time.time()))  # 时间戳

    # 计算sign
    txt = "orderId=" + order_id + "&" + "secret=" + secret + "&" + "time=" + time_str
    sign = hashlib.md5(txt.encode()).hexdigest()
    # 访问URL获取IP
    url = (
            "http://api.hailiangip.com:8422/api/getIp?type=1" + "&num=" + num + "&pid=" + pid
            + "&unbindTime=" + unbind_time + "&cid=" + cid
            + "&orderId=" + order_id + "&time=" + time_str + "&sign=" + sign + "&dataType=0"
            + "&lineSeparator=" + lineSeparator + "&noDuplicate=" + noDuplicate + "&singleIp=" + singleIp)
    my_response = requests.get(url).content
    js_res = json.loads(my_response)
    for dic in js_res["data"]:
        try:
            ip = dic["ip"]
            port = dic["port"]
            ip_port = ip + ":" + str(port)
            return ip_port
        except BaseException as e:
            logger.error("获取ip地址异常:{}", e)
            return None


if __name__ == '__main__':
    order_id = ''
    secret = ''
    unbind_time = str(60 * 10)
    ip = get_proxy_api(order_id, secret, unbind_time)
    print(ip)
