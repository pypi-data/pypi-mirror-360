from xtquant import xtdata
import pandas as pd
from loguru import logger


# 获取股票实时行情数据
def get_qmt_real_time_quotes(symbol_list):
    try:
        res = xtdata.get_full_tick(symbol_list)
        records = []
        for symbol, stock_data in res.items():
            record = stock_data.copy()  # 创建字典副本避免修改原始数据
            record['symbol'] = symbol  # 添加股票代码列
            records.append(record)  # 添加到列表
        # 一次性转换为DataFrame
        df = pd.DataFrame(records)
        return df
    except BaseException as e:
        logger.error("获取实时行情出现异常:{}", e)


if __name__ == '__main__':
    symbol_list_test = ['600519.SH', '300085.SZ', '000001.SZ']
    get_qmt_real_time_quotes(symbol_list_test)
