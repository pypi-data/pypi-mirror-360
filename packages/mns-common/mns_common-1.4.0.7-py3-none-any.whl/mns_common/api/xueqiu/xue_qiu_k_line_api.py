import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import requests
import pandas as pd


# year 年
#  quarter 季度
# month 月度
# week 周
# day 日
def get_xue_qiu_k_line(symbol, period, cookie, end_time, hq):
    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json"

    params = {
        "symbol": symbol,
        "begin": end_time,
        "period": period,
        "type": hq,
        "count": "-120084",
        "indicator": "kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://xueqiu.com",
        "priority": "u=1, i",
        "referer": "https://xueqiu.com/S/SZ300879?md5__1038=n4%2BxgDniDQeWqxYwq0y%2BbDyG%2BYDtODuD7q%2BqRYID",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "cookie": cookie
    }

    response = requests.get(
        url=url,
        params=params,
        headers=headers
    )

    if response.status_code == 200:
        response_data = response.json()
        df = pd.DataFrame(
            data=response_data['data']['item'],
            columns=response_data['data']['column']
        )







        # 1. 转换为 datetime（自动处理毫秒级时间戳）
        df["beijing_time"] = pd.to_datetime(df["timestamp"], unit="ms")

        # 2. 设置 UTC 时区
        df["beijing_time"] = df["beijing_time"].dt.tz_localize("UTC")

        # 3. 转换为北京时间（UTC+8）
        df["beijing_time"] = df["beijing_time"].dt.tz_convert("Asia/Shanghai")

        # 4. 提取年月日（格式：YYYY-MM-DD）
        df["str_day"] = df["beijing_time"].dt.strftime("%Y-%m-%d")
        del df["beijing_time"]

        return df
    else:
        # 直接抛出带有明确信息的异常
        raise ValueError("调用雪球接口失败")


if __name__ == '__main__':
    number = 1
    cookies = 'cookiesu=431747207996803; device_id=e7bd664c2ad4091241066c3a2ddbd736; xq_is_login=1; u=9627701445; s=ck12tdw0na; bid=7a2d53b7ab3873ab7ec53349413f0a21_mb9aqxtx; xq_a_token=9367502e9138a95092fac9fb24c5348edb095013; xqat=9367502e9138a95092fac9fb24c5348edb095013; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjk2Mjc3MDE0NDUsImlzcyI6InVjIiwiZXhwIjoxNzUyMDM2NTM4LCJjdG0iOjE3NDk0NDQ1MzgzMDgsImNpZCI6ImQ5ZDBuNEFadXAifQ.rKuCHOgTHaMp0wRkvkPjNz8YrV6oia1xVAY35MmlYPlTvIYDEqsxqI3Qyz2dh5UuBC4TSlJUmVOEbvZzrM990-RaqT1rYCPjHaAZo4qDsOz34ypEAXJBzYaz32KPTGbM9lDwOFuHxeSUFeM0R-2Lhe3UbmRPU_zEBneuCQ_vrz4DkM98qswZ9emA3B8mty-Qa-40NrCb0xLZ52Oi8VKwEJXoPmlsEE3D2vxB0v0qEaKDjBSanCpe0mHCE4ds1yHaZvfV2zSRl1PYcCF85yiCtba3jYkQJ4lR2hmk9AyYOAtnQ-1aiYGjgNpe9ETJGvnoG_o3WUJmFFl0nAENqvviNQ; xq_r_token=59ae4e9f9cc1ed66343ff1e68a7b32c0d8c27983; Hm_lvt_1db88642e346389874251b5a1eded6e3=1749548204,1749603966,1749606594,1749630748; HMACCOUNT=16733F9B51C8BBB0; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1749630957; ssxmod_itna=QqjOAKYIwGkYDQG0bGCYG2DmxewDAo40QDXDUqAQtGgnDFqAPDODCOG/iwQEgM8DbPKitDD5bh9xGXPmDA5DnGx7YDtr49v+i9gGB+eQpcAb4bRGApg4OQXWWOYB0hOEBDpAav72v1mDB3DbqDyKiIuB4GGf4GwDGoD34DiDDpfD03Db4D+nWrD7ORQMluokePDQ4GyDitQigWDA4DjIQx+G7bOPnbYDDNYeK+eIfYODYpogW0FrxqDAkDtgkbDjkPD/SGjcPDBnIkYepuEgqOp8CcaxBQD7dF=oeq8jmWNaegu/YNVBbIwCDIQGeWm3lxYWDVQG3WxOmDKID5CI3WmeYqqnDOGYu0PNb4DDPoWDbYxH/GeohS85lImlA5ot+Q0qDLizW+KaRxKoU8G08DUY2D9rN/riYGxtiqKOqxhKND+/HPeD; ssxmod_itna2=QqjOAKYIwGkYDQG0bGCYG2DmxewDAo40QDXDUqAQtGgnDFqAPDODCOG/iwQEgM8DbPKitDD5bhYxD3betID4WDLDlGWvDBq9DE0336bqjR87=Rad7dn=250R0FgdQyhaMthWK7TYTInPnkD/bGDDkB3YUTfXD4dyGD0AKw=fKlNSjmXgKBLeBgr9+CGx1qKqopRQHDtQ1daQVMwqWPa2+Z32+QuOaZc3WZXW=Pa821DB9ZXe30HfGwBv28yHVY7EmEY8yPcmMfMEMR6in3XQkYh0uCDLybC=hOxU/YkDdfxP1NRN3bLXK61i4z6hz1rKi7sBTQZ2Wjw33+O78=tSTK8dwbrKh==4+7RidD+4exl2+4Mb+Q1TobeGFsr7iGembt2QblAYrbKqDrRjsqYN9evSeQFk3tErsGdtAOsS3PgACx1mGe0mf2C5ZB5xhDKBD=7fsaKsP44D'
    while True:
        test_df = get_xue_qiu_k_line('SZ000001', 'day', cookies, '1749744000000', 'after')
        print(number)
        number = number + 1
