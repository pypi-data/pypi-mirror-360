import numpy as np
import pandas as pd
from hhsqllib.corefunc import *
from hhsqllib.sqlfile import *
from hhsqllib.sqlconnect import *


freq_dict = {'m':12,'w':52,'d':252}

import pandas as pd
from numpy.lib.stride_tricks import as_strided as stride

import time
from functools import wraps
def timer(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start = time.perf_counter()
        result = func(self, *args, **kwargs)
        end = time.perf_counter()
        class_name = self.__class__.__name__
        print(f"{class_name}.{func.__name__} 执行时间: {end - start:.6f} 秒")
        return result
    return wrapper




def roll(df, w, **kwargs):
    """[rolling for multicolumns]

    Arguments:
        df {[pd.DataFrame]} -- [the input dataframe]
        w {[int]} -- [rolling window]

    Returns:
        [pd.Group] -- [sth group]
    """

    v = df.values
    d0, d1 = v.shape
    s0, s1 = v.strides

    a = stride(v, (d0 - (w - 1), w, d1), (s0, s0, s1))

    rolled_df = pd.concat({
        row: pd.DataFrame(values, columns=df.columns)
        for row, values in zip(df.index[-a.shape[0]:], a)
    })

    return rolled_df.groupby(level=0, **kwargs)



class factortool:

    def factor_check(self, factor = None):

        # step1 检查列名是不是包含 'sid', 'dt', 'factor_value'
        required_columns = ['sid', 'dt', 'factor_value']
        missing_columns = [col for col in required_columns if col not in factor.columns]
        if not missing_columns:
            print("所有必要列都存在。")
            return True
        else:
            print(f"缺少以下列: {missing_columns}")
            return False

    # 返回交易日序列
    def get_trade_dt(self,dts=None, dte=None, offset='first', period='M'):
        '''
        Args:
            dts: 开始日期 默认为 19910101
            dte: 结束日期 默认为 当前日期
            sourcedb: 数据源
            offset: first 取左，last 取右 默认为 取左
            period: 取数周期
        Returns:
        '''
        if dts is None:
            dts = '19910101'
        if dte is None:
            dte = datetime.datetime.now().strftime("%Y%m%d")
        with pd.HDFStore(self.localfile, 'r') as store:
            df = store.select('tradedate', where='TRADE_DAYS >= \'%s\' and TRADE_DAYS <= \'%s\'' % ( dts,dte))
        df['dt'] = pd.to_datetime(df.TRADE_DAYS)
        df.set_index('dt', inplace=True)
        dfresample = df.resample(period)
        tddt = dfresample.agg(offset)
        return tddt[['TRADE_DAYS']]

    def get_citic_indu_levelone(self):
        """

        Returns: 返回中信一级行业

        """
        with pd.HDFStore(self.localfile, 'r') as store:
            df = store.select('citicindulevelone')
        return df[['INDEX_INFO_WINDCODE', 'sid', 'S_CON_INDATE', 'S_CON_OUTDATE',
       'INDEX_INFO_NAME', 'S_INFO_NAME', 'S_INFO_DELISTDATE',
       'S_INFO_LISTDATE']]

    def get_eodindicator(self, dts=None, dte=None, sid = None):
        """
        Args:
            dts: 开始时间
            dte: 结束时间
            sid: 股名
        Returns: 返回 eodindicator
        """
        if sid is None:
            with pd.HDFStore(self.localfile, 'r') as store:
                df = store.select('eodindicator', where='dt >= \'%s\' and dt <= \'%s\'' % ( dts,dte))
        else:
            with pd.HDFStore(self.localfile, 'r') as store:
                df = store.select('eodindicator', where='dt >= \'%s\' and dt <= \'%s\' and sid == \'%s\'' % ( dts,dte,sid))
        return df


    def get_eodprice(self, dts=None, dte=None, sid = None):
        """
        Args:
            dts: 开始时间
            dte: 结束时间
            sid: 股名
        Returns: 返回 eodpric
        """
        if sid is None:
            with pd.HDFStore(self.localfile, 'r') as store:
                df = store.select('eodprice', where='dt >= \'%s\' and dt <= \'%s\'' % (dts, dte))
        else:
            with pd.HDFStore(self.localfile, 'r') as store:
                df = store.select('eodprice',
                                  where='dt >= \'%s\' and dt <= \'%s\' and sid == \'%s\'' % (dts, dte, sid))
        return df
