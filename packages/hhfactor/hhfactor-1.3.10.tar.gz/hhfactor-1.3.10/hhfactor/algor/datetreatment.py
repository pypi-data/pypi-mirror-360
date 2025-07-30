from abc import ABCMeta, abstractmethod
import pandas as pd
from functools import lru_cache
import os
from itertools import chain
import pandas as pd

def dt_handle(date):
    try:
        return pd.to_datetime(date).strftime('%Y%m%d')
    except ValueError:
        return date

    # 这个要作到说明文档中


import json

def china_td(datelist = None):
    """获取所有交易日
    Returns:
        list of 'trade_dt'
    """
    def load_list_from_file(filename='tradedate.json'):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []  # 如果文件不存在，返回空列表
    if isinstance(datelist, list):
        return datelist
    else:
        import pkg_resources
        data_path = pkg_resources.resource_filename('hhfactor', 'data/tradedate.json')
        return load_list_from_file(filename=data_path)

dict_td = {
    'cn': china_td,
}


def mixin_trade_dt():
    lst = list(set(chain(*(dict_td[k]() for k in ['cn']))))
    lst.sort()
    return pd.DataFrame(data=lst, columns=['trade_dt'])



def get_all_trade_dt():
    """[获取所有交易日]

    Returns:
        [pd.DataFrame] -- [dataframe with columns of 'trade_dt']
    """
    return mixin_trade_dt()


def get_trade_dt_list(begin_dt='19900101', end_dt='20990101', astype='list'):
    """[获取指定时间段的所有交易日]

    Keyword Arguments:
        begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
        end_dt {str or datetime} -- [end_dt] (default: {'20990101'})
        astype {str} -- [list or pd] (default: {'list'})

    Raises:
        ValueError -- [f"astype:{astype} must be 'pd' or 'list'!"]

    Returns:
        [pd.DataFrame or list] -- [trade_dts between begin_dt and end_dt]
    """

    df = get_all_trade_dt()
    tmp_df = df.copy()
    begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
    tmp_df = tmp_df[(tmp_df['trade_dt'] >= begin_dt)
                    & (tmp_df['trade_dt'] <= end_dt)]
    if astype == 'pd':
        return tmp_df
    elif astype == 'list':
        return tmp_df['trade_dt'].tolist()
    else:
        raise ValueError(f"astype:{astype} must be 'pd' or 'list'!")



def adjust_trade_dt(date, adjust='last'):
    """[adjust trade_dt]

    Arguments:
        date {[str or datetime]} -- [date]

    Keyword Arguments:
        adjust {str} -- [last or next] (default: {'last'})

    Raises:
        ValueError -- [f"adjust:{adjust} must be 'last' or 'next'!"]

    Returns:
        [str] -- [adjusted trade_dt with %Y%m%d type]
    """

    t_df = get_all_trade_dt()
    date = dt_handle(date)
    if adjust == 'last':
        t_df = t_df[t_df['trade_dt'] <= date]
        return t_df['trade_dt'].iloc[-1]
    elif adjust == 'next':
        t_df = t_df[t_df['trade_dt'] >= date]
        return t_df['trade_dt'].iloc[0]
    else:
        raise ValueError(f"adjust:{adjust} must be 'last' or 'next'!")



def step_trade_dt(date, step=1):
    """[step trade_dt]

    Arguments:
        date {[str or datetime]} -- [date]

    Keyword Arguments:
        step {int} -- [step] (default: {1})

    Returns:
        [str] -- [date with %Y%m%d type]
    """

    t_df = get_all_trade_dt()
    date = dt_handle(date)
    if step >= 0:
        try:
            return t_df[t_df['trade_dt'] >= date]['trade_dt'].iloc[step]
        except IndexError:
            return t_df['trade_dt'].iloc[-1]
    elif step < 0:
        try:
            return t_df[t_df['trade_dt'] < date]['trade_dt'].iloc[step]
        except IndexError:
            return t_df['trade_dt'].iloc[0]



def delta_trade_dt(begin_dt, end_dt):
    """[get length of trade_dt, include begin_dt and end_dt]

    Arguments:
        begin_dt {[str or datetime]} -- [begin_dt]
        end_dt {[tstr or datetime]} -- [end_dt]

    Returns:
        [int] -- [len of date_range]
    """

    t_df = get_all_trade_dt()
    begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
    return len(
        t_df[(t_df['trade_dt'] >= begin_dt) & (t_df['trade_dt'] <= end_dt)])



class RefreshBase(metaclass=ABCMeta):
    """获取调仓日期的基类

    Attributes:
        *args: -1 or 1, int or (1, -1)
    """

    def __init__(self, *args):
        if abs(sum(args)) > 1:
            raise ValueError('args must be 1 or -1')
        self.args = sorted(args, reverse=True)

    @abstractmethod
    def get(self, begin_dt, end_dt):
        pass

    @lru_cache()
    def next(self, date, step=1, adjust=True):
        """[get next date, 20180921 -> 20180928(Monthly(-1))]

        Arguments:
            date {[str or datetime]} -- [date]
            adjust {[bool]} -- [if adjust & date is the key day, pass]
            step {[int]} -- [step numbers]

        Returns:
            [str] -- [next day in class frequency]
        """

        end_dt = step_trade_dt(date, 600)
        df = self.get(date, end_dt).tolist()
        try:
            if df[0] == date:
                if adjust:
                    return df[step]
            return df[step-1]
        except IndexError:
            return df[-1]

    @lru_cache()
    def prev(self, date, step=1, adjust=True):
        """[get previous day, 20180921 -> 20180831(Monthly(-1))]

        Arguments:
            date {[str or datetime]} -- [date]
            adjust {[bool]} -- [if adjust & date is the key day, pass]
            step {[int]} -- [step numbers]

        Returns:
            [str] -- [previous day in class frequency]
        """

        begin_dt = step_trade_dt(date, -600)
        df = self.get(begin_dt, date).tolist()
        try:
            if df[-1] == date:
                if adjust:
                    return df[-1-step]
            return df[-step]
        except IndexError:
            return df[0]

    @staticmethod
    def freq_handle(arg, df, step=1):
        if arg == 1:
            tmp_df = df['trade_dt'].apply(
                lambda x: adjust_trade_dt(x[:6] + '01', 'next'))
        elif arg == -1:
            tmp_df = df['trade_dt'].apply(
                lambda x: step_trade_dt(str(int(x[:6]) + step) + '01', -1))

        return tmp_df

    @staticmethod
    def df_handle(begin_dt='19900101', end_dt='20990101', func=None):
        begin_dt = dt_handle(begin_dt)
        end_dt = dt_handle(end_dt)
        df = get_trade_dt_list(begin_dt, end_dt, astype='pd').copy()

        df['trade_dt'] = df['trade_dt'].apply(func)
        df.drop_duplicates(inplace=True)
        return df

    def _get(self,
             begin_dt='19900101',
             end_dt='20990101',
             func=None,
             offset=None):
        begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
        df = get_trade_dt_list(
            step_trade_dt(begin_dt, -1 * offset),
            step_trade_dt(end_dt, offset),
            astype='pd').copy()
        df['_trade_dt'] = pd.to_datetime(df['trade_dt'])
        df['month'] = df['_trade_dt'].map(func)
        all_trade_dt = pd.Series()
        for arg in self.args:
            if arg == 1:
                tmp_df = df.drop_duplicates('month', keep='first')['trade_dt']
            elif arg == -1:
                tmp_df = df.drop_duplicates('month', keep='last')['trade_dt']
            all_trade_dt = pd.concat([all_trade_dt, tmp_df])
        all_trade_dt.sort_values(inplace=True)
        all_trade_dt = all_trade_dt[
            (all_trade_dt >= begin_dt)
            & (all_trade_dt <= end_dt)].drop_duplicates()
        return all_trade_dt


class Daily(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]

        Arguments:
            RefreshBase {[cls]} -- [refreshbase]

        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})

        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        return get_trade_dt_list(
            begin_dt,
            end_dt,
            astype='pd')['trade_dt'].copy()


class Monthly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]

        Arguments:
            RefreshBase {[cls]} -- [refreshbase]

        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})

        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        def func(x):
            return f"{x.year}{x.month}"

        return self._get(
            begin_dt=begin_dt, end_dt=end_dt, func=func, offset=40)


class Weekly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]

        Arguments:
            RefreshBase {[cls]} -- [refreshbase]

        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})

        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        def func(x):
            return f"{x.year}{x.week}"

        return self._get(
            begin_dt=begin_dt, end_dt=end_dt, func=func, offset=20)


class BiWeekly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]

        Arguments:
            RefreshBase {[cls]} -- [refreshbase]

        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})

        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        all_trade_dt = pd.Series()
        for arg in self.args:
            if arg == 1:
                tmp_df = Weekly(1).get(begin_dt, end_dt)[::2]
            elif arg == -1:
                tmp_df = Weekly(-1).get(begin_dt, end_dt)[::2]
            all_trade_dt = pd.concat([all_trade_dt, tmp_df])
        all_trade_dt.sort_values(inplace=True)
        all_trade_dt.drop_duplicates(inplace=True)
        return all_trade_dt


class Quarterly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]

        Arguments:
            RefreshBase {[cls]} -- [refreshbase]

        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})

        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        def func(x):
            return f"{x.year}{x.quarter}"

        return self._get(
            begin_dt=begin_dt, end_dt=end_dt, func=func, offset=120)


class Reportly(RefreshBase):
    @staticmethod
    def _report(x):
        if x <= x[:4] + '0430':
            return str(int(x[:4]) - 1) + '11'
        elif x <= x[:4] + '0831':
            return x[:4] + '05'
        elif x <= x[:4] + '1031':
            return x[:4] + '09'
        elif x <= x[:4] + '1231':
            return x[:4] + '11'

    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]

        Arguments:
            RefreshBase {[cls]} -- [refreshbase]

        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})

        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
        df = self.df_handle(begin_dt, end_dt, self._report)
        all_trade_dt = pd.Series()
        for arg in self.args:
            if arg == 1:
                tmp_df = df['trade_dt'].apply(
                    lambda x: adjust_trade_dt(x[:6] + '01', 'next'))
            elif arg == -1:

                def neg_report(x):
                    if x[-2:] == '11':
                        return step_trade_dt(str(int(x[:4]) + 1) + '0501', -1)
                    elif x[-2:] == '09':
                        return step_trade_dt(x[:4] + '1101', -1)
                    elif x[-2:] == '05':
                        return step_trade_dt(x[:4] + '0901', -1)

                tmp_df = df['trade_dt'].apply(neg_report)
            all_trade_dt = pd.concat([all_trade_dt, tmp_df])
        all_trade_dt.sort_values(inplace=True)
        # all_trade_dt = pd.to_datetime(all_trade_dt)
        return all_trade_dt[(all_trade_dt >= begin_dt)
                            & (all_trade_dt <= end_dt)]


class Yearly(RefreshBase):
    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]

        Arguments:
            RefreshBase {[cls]} -- [refreshbase]

        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})

        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        def func(x):
            return f"{x.year}"

        return self._get(
            begin_dt=begin_dt, end_dt=end_dt, func=func, offset=300)


class Halfyearly(RefreshBase):
    @staticmethod
    def _year(x):
        if x <= x[:4] + '0630':
            return x[:4] + '01'
        elif x <= x[:4] + '1231':
            return x[:4] + '07'

    def get(self, begin_dt='19900101', end_dt='20990101'):
        """[get trade_dt Series with class freq]

        Arguments:
            RefreshBase {[cls]} -- [refreshbase]

        Keyword Arguments:
            begin_dt {str or datetime} -- [begin_dt] (default: {'19900101'})
            end_dt {str or datetime} -- [end_dt] (default: {'20990101'})

        Returns:
            [pd.Series] -- [trade_dt Series]
        """

        begin_dt, end_dt = dt_handle(begin_dt), dt_handle(end_dt)
        df = self.df_handle(begin_dt, end_dt, self._year)
        all_trade_dt = pd.Series()
        for arg in self.args:
            tmp_df = self.freq_handle(arg, df, 6)
            all_trade_dt = pd.concat([all_trade_dt, tmp_df])
        all_trade_dt.sort_values(inplace=True)
        return all_trade_dt[(all_trade_dt >= begin_dt)
                            & (all_trade_dt <= end_dt)]


if __name__ == '__main__':
    m = Monthly(-1)
    lst = m.get()
    step = 2
    print(m.next('20161220', step=step), m.prev('20161220', step=step))
