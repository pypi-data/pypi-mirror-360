import numpy as np
import pandas as pd
from hhsqllib.corefunc import *
from hhsqllib.sqlfile import *
from hhsqllib.sqlconnect import *
from hhsqllib.corefunc import corefunc
from ..factor import Factor

freq_dict = {'m': 12, 'w': 52, 'd': 252}

def factor_check(factor):
    # step1 检查列名是不是包含 'sid', 'dt', 'factor_value'
    required_columns = ['sid', 'dt', 'factor_value']
    missing_columns = [col for col in required_columns if col not in factor.columns]
    if not missing_columns:
        print("所有必要列都存在。")
        return True
    else:
        print(f"缺少以下列: {missing_columns}")
        return False

def factor_addindumv(factor=None, dbo=None, dts='20100101', dte='20241101', freq='m', offset='first'):
    # step1 删除 sid 和 dt 为na的
    if isinstance(dbo, Factor):
        tradedt = dbo.get_trade_dt(dts=dts, dte=dte, period=freq, offset=offset)
        indu = dbo.get_citic_indu_levelone()
        mv = dbo.get_eodindicator(dts=dts, dte=dte).set_index(['dt', 'sid'])[['val_mv']]
        eodprice = dbo.get_eodprice(dts=dts, dte=dte).set_index(['dt', 'sid'])
    elif isinstance(dbo, DataBase):
        tradedt = corefunc.get_trade_dt(dts=dts, dte=dte, sourcedb=dbo, period=freq, offset=offset)
        indu = corefunc.get_citic_indu_levelone(sourcedb=dbo)
        mv = corefunc.get_eodindicator(dts=dts, dte=dte, sourcedb=dbo).set_index(['dt', 'sid'])[['val_mv']]
        eodprice = corefunc.get_eodprice(dts=dts, dte=dte, sourcedb=dbo).set_index(['dt', 'sid'])
    elif isinstance(dbo, dict):
        tradedt = dbo['tradedt']
        indu = dbo['indu']
        mv = dbo['mv']
        eodprice = dbo['eodprice']
    else:
        assert 1, "dbo 是一个错误的类型"


    factor.dropna(subset=['sid', 'dt'], inplace=True)
    # step2 按照frep合并交易日
    # step3 合并因子
    factor = tradedt.merge(factor, left_on='TRADE_DAYS', right_on='dt')
    # step4 合并行业
    factor = factor.merge(indu[['sid', 'INDEX_INFO_WINDCODE', 'S_CON_INDATE', 'S_CON_OUTDATE']].fillna('20990101'),
                          how='left', on='sid')
    factor = factor[(factor['dt'] >= factor['S_CON_INDATE']) & (factor['dt'] <= factor['S_CON_OUTDATE'])]

    # step5 合并市值
    factor = factor[['sid', 'dt', 'factor_value', 'INDEX_INFO_WINDCODE']]

    factor = factor.set_index(['dt', 'sid'])[['factor_value', 'INDEX_INFO_WINDCODE']]
    factor.sort_index(inplace=True)
    factor = factor.join(mv)

    factor.index = factor.index.set_levels([pd.to_datetime(factor.index.levels[0].astype(str)), factor.index.levels[1]])
    # step5 将市值和行业为空的删除
    factor.dropna(subset=['INDEX_INFO_WINDCODE', 'val_mv'], inplace=True)
    # step6 处理eodprice 包括次日的开盘价，能不能交易，和当日收盘价
    eodprice['updownlimit'] = (eodprice['S_DQ_OPEN'] > eodprice['S_DQ_STOPPING']) & (
                eodprice['S_DQ_OPEN'] < eodprice['S_DQ_LIMIT'])& (
                eodprice['S_DQ_VOLUME'] > 100)

    # step6 处理eodprice 包括次日的开盘价，能不能交易，和当日收盘价
    eodprice['updownlimit'] = (eodprice['S_DQ_OPEN'] > eodprice['S_DQ_STOPPING']) & (
            eodprice['S_DQ_OPEN'] < eodprice['S_DQ_LIMIT']) & (
                                      eodprice['S_DQ_VOLUME'] > 100)

    # 第二日开盘价
    nextopen = eodprice['S_DQ_ADJOPEN'].unstack().shift(-1).stack().to_frame('next_open')
    # 第二日是不是可以交易
    nextlowuplimit = eodprice['updownlimit'].unstack().shift(-1).stack().to_frame('next_updownlimit')
    # 如果第二日不可以交易，往后递延，但递延不超过4个交易日
    nexttrade = nextopen.join(nextlowuplimit)
    nexttrade0 = nexttrade[nexttrade['next_updownlimit']].next_open.unstack()
    nexttrade0.fillna(method='bfill', inplace=True, limit=4)
    nextopen = nexttrade0.stack().to_frame('next_open')
    # 合并交易日收盘价
    nexttrade = nextopen.join(eodprice['S_DQ_ADJCLOSE'].to_frame('adjclose'))
    nexttrade.index = nexttrade.index.set_levels(
        [pd.to_datetime(nexttrade.index.levels[0].astype(str)), nexttrade.index.levels[1]])

    pctchange1 = nexttrade.next_open.unstack().reindex(factor.index.levels[0]).pct_change(fill_method=None).shift(-1).stack().to_frame('nextadjopenpct')
    pctchange2 = nexttrade.adjclose.unstack().reindex(factor.index.levels[0]).pct_change(fill_method=None).shift(-1).stack().to_frame('adjclosepct')

    # step7 合并价格
    factor = factor.join(pctchange1).join(pctchange2)

    return factor


# 处理因子na值问题
def fillna(factor_resample=None, method='drop'):
    '''

    Args:
        factor_resample: 原始data
        method: drop 为直接剔除
        0：为填充0
        mean：为用行业均值填充
        median：为用行业中位数填充
    Returns:
        处理好nan值的dataframe
    '''
    if not method in [0, 'drop', 'mean', 'median']:
        raise Exception("freq 参数错误，只支持以下选项之一 0,'drop', 'mean', 'median'。")
    if method == 'drop':
        factor_resample = factor_resample.dropna(subset='factor_value')
    elif method == 0:
        factor_resample['factor_value'] = factor_resample['factor_value'].fillna(0)
    elif method == 'mean':
        factor_resample['factor_value'] = factor_resample.groupby(['dt', 'INDEX_INFO_WINDCODE']).apply(
            lambda x: (x.factor_value.fillna(x.factor_value.mean()))).droplevel(level=[0, 1])
    elif method == 'median':
        factor_resample['factor_value'] = factor_resample.groupby(['dt', 'INDEX_INFO_WINDCODE']).apply(
            lambda x: (x.factor_value.fillna(x.factor_value.median()))).droplevel(level=[0, 1])
    return factor_resample


# 中位数法去除极值
def factor_detremmad(factor_resample=None, ifkeep=True, col='factor_value', level=5):
    # factor_resample.rename(columns={col: 'factor_value'},inplace=True)
    '''
    Args:
        factor_resample:
        ifkeep: 如果是true 那么用 上下限替代，如果是false那么用nan替代
    Returns:
    '''
    # def middeextreme(x):
    #     x_mid = x.factor_value.median()
    #     dm = abs(x.factor_value - x_mid).median()
    #     upper_bound = x_mid + 5.2 * dm
    #     lower_bound = x_mid - 5.2 * dm
    #     u_x = upper_bound if ifkeep else np.nan
    #     l_x = lower_bound if ifkeep else np.nan
    #     x.factor_value = np.where(x.factor_value > upper_bound, u_x, x.factor_value)
    #     x.factor_value = np.where(x.factor_value < lower_bound, l_x, x.factor_value)
    #     return x.factor_value.droplevel(0)
    return factor_resample.groupby('dt').apply(lambda x: winsorize(x[col], level=level, ifkeep=ifkeep).droplevel(0))


# winsorize 分位数截尾法
def winsorize(df0=None, level=3, ifkeep=True):
    df_ = df0.round(10)

    def _winsorize(x, ifkeep, level):
        x_mid = x.median()
        dm = abs(x - x_mid).median()
        upper_bound = x_mid + level * dm
        lower_bound = x_mid - level * dm
        u_x = upper_bound if ifkeep else np.nan
        l_x = lower_bound if ifkeep else np.nan
        x = x.mask(x >= upper_bound, u_x)
        x = x.mask(x <= lower_bound, l_x)
        return x

    if df_.empty:
        return df_
    # 防止出现无限递归
    df_ = _winsorize(x=df_, level=level, ifkeep=ifkeep)
    factor_std = df_.std()
    # 如果标准差为0，如果某一列的标准差为0（意味着该列的所有值都相同），对不是同一个值的数做分位数截尾法
    if isinstance(factor_std, float):
        if round(factor_std, 3) == 0.0:
            return winsorize(df0[df0 != df_.max()])._append(
                df0[df0 == df_.max()]).reindex(df0.index)
    return df_


def factor_zscore(factor_resample=None, col='factor_value'):
    factor_resample = factor_resample.rename(columns={col: 'factor_value'})

    def zscore(x):
        x_mean = x.factor_value.mean()
        x_std = x.factor_value.std()
        factorvalue_ = (x.factor_value - x_mean) / x_std
        return factorvalue_.droplevel(0)

    return factor_resample.groupby('dt').apply(zscore)


def zscore(df, ddof=0):
    return (df - df.mean()) / df.std(ddof=ddof)


def mvquantile(df, n=50):
    return ((n * df.rank() / (df.count() + 1)).astype(int) + 1)


def factor_neutralization(df=None, col=['val_mv'], factorname='factor_value'):
    df = df.rename(columns={factorname: 'factor_value'})
    import statsmodels.api as sm
    def neutralization(df_, col):
        # 仅行业中性化
        if col == []:
            dfr = pd.get_dummies(df_, columns=['INDEX_INFO_WINDCODE'], dtype=int)
            X = dfr[[col for col in dfr.columns if col.startswith('INDEX_INFO_WINDCODE_')]]
            y = dfr['factor_value']
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()
            # 提取残差
            return model.resid.droplevel(0)
        # 市值和行业中性化
        elif col == ['val_mv']:
            dfr = pd.get_dummies(df_, columns=['INDEX_INFO_WINDCODE'], dtype=int)
            dfr['log_mv'] = np.log(dfr['val_mv'])
            dfr['log_mv'] = zscore(dfr['log_mv'])
            X = dfr[['log_mv'] + [col for col in dfr.columns if col.startswith('INDEX_INFO_WINDCODE_')]]
            y = dfr['factor_value']
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()
            # 提取残差
            return model.resid.droplevel(0)
        # 行业 + 按照指定的因子中性化
        else:
            dfr = pd.get_dummies(df_, columns=['INDEX_INFO_WINDCODE'], dtype=int)
            for coli in col:
                if coli == 'val_mv':
                    dfr['val_mv'] = np.log(dfr['val_mv'])
                    dfr['val_mv'] = zscore(dfr['val_mv'])
                else:
                    dfr[coli] = winsorize(df0=dfr[coli], level=3, ifkeep=True)
                    dfr[coli] = zscore(dfr[coli])

            X = dfr[col + [col0 for col0 in dfr.columns if col0.startswith('INDEX_INFO_WINDCODE_')]]
            y = dfr['factor_value']
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()
            # 提取残差
            return model.resid.droplevel(0)

    return df.groupby('dt').apply(neutralization, col)


def factor_clean(factor_resample=None, method='drop', ifkeep=True):
    # 处理缺失值
    factor_resample = fillna(factor_resample=factor_resample, method=method)
    # 将极端值用上下限替代 ， 如果 ifkeep = False，那么删除
    factor_resample['factor_value'] = factor_detremmad(factor_resample=factor_resample, ifkeep=ifkeep)
    factor_resample.dropna(subset='factor_value', inplace=True)
    # 将因子进行归一化处理
    factor_resample['factor_value'] = factor_zscore(factor_resample=factor_resample)
    # 将次日没有开盘或者收盘股价变化
    factor_resample.dropna(subset=['nextadjopenpct', 'adjclosepct'], inplace=True)
    # 因子中性化
    factor_resample['factor_value'] = factor_neutralization(df=factor_resample)
    # 去除空值因子
    factor_resample.dropna(subset=['factor_value'], inplace=True)

    # 剔除有效因子太少的情况
    # c = factor_resample.groupby('dt')['factor_value'].count()
    # factor_resample = factor_resample.loc[c.loc[(c > c.quantile(0.05))].index]

    return factor_resample


def groupdiagnosis(n=10, factor_resample=None):
    def factorquantile(df_, n=None):
        return ((n * df_['factor_value'].rank() / (df_['factor_value'].count() + 1)).astype(int) + 1).astype(
            str).droplevel(0)

    factor_resample['factorvalue_quantile'] = factor_resample.groupby('dt').apply(factorquantile, (n))


    # 这里筛选只有第二天可以交易的股票
    # factor_resample_qr = factor_resample[factor_resample['next_updownlimit']]

    factor_resample_qr = factor_resample.copy()

    benchmark = (factor_resample_qr.nextadjopenpct.unstack()).mean(axis=1).shift(1)
    group_resdict = {}
    for i in range(1, n + 1):
        portfolio = factor_resample_qr[factor_resample_qr['factorvalue_quantile'] == '%d' % i]
        portfolio_ = (portfolio.factorvalue_quantile.unstack()).astype(float)
        portfolio_turnover = 1 - (abs(portfolio_.diff()).count(axis=1) / portfolio_.count(axis=1)).iloc[1:]
        portfolio_pct = (portfolio.nextadjopenpct.unstack()).astype(float)
        portfolio_info = portfolio_pct.mean(axis=1).shift(1).to_frame('MeanReturn')
        portfolio_info = portfolio_info.join(portfolio_turnover.to_frame('turnoverratio'))
        portfolio_info['exfeereturn'] = portfolio_info['MeanReturn'] - 0.001 * portfolio_info['turnoverratio']
        portfolio_info['benchmark'] = benchmark
        group_resdict[i] = portfolio_info
    return group_resdict


def indexmemberseries(indexcode='000300.SH', dbo=None):
    dfindex = corefunc.get_index_members(indexs=[indexcode], sourcedb=dbo)
    dfindex['S_CON_OUTDATE'] = dfindex['S_CON_OUTDATE'].fillna(datetime.datetime.now().strftime("%Y%m%d"))
    dfindex['dt'] = dfindex.apply(lambda x: pd.date_range(x.S_CON_INDATE, x.S_CON_OUTDATE).strftime("%Y%m%d"), axis=1)
    return dfindex.explode('dt')


def coverratiodescripe(factor0=None):
    coverseries = factor0.groupby('dt')['factor_value'].count() / factor0.groupby('dt')['indexcode'].count()
    coverseries = coverseries[coverseries != 0]
    return coverseries.describe()


from scipy.stats import spearmanr, pearsonr


def calcuic(df_):
    spearman_corr, p_value = spearmanr(df_['factor_value'], df_['adjclosepct'])
    return pd.Series([spearman_corr, p_value], index=['spearman_corr', 'spearman_corr_p'])


def factordiagnosis(n=10, factor_resample=None):
    def regression_(df_):
        import statsmodels.api as sm
        dfr = pd.get_dummies(df_, columns=['INDEX_INFO_WINDCODE'], drop_first=True, dtype=int)
        dfr['log_mv'] = np.log(dfr['val_mv'])
        X = dfr[
            ['factor_value', 'log_mv'] + [col for col in dfr.columns if col.startswith('INDEX_INFO_WINDCODE_')]]
        y = dfr['adjclosepct']
        X = sm.add_constant(X)
        weights = np.sqrt(dfr['val_mv'])
        model = sm.WLS(y, X, weights=weights).fit()
        variable = 'factor_value'
        coef_value = model.params[variable]
        t_value = model.tvalues[variable]
        return pd.Series([coef_value, t_value], index=['factor_core', 'factor_tvalue'])

    regression_res = factor_resample.groupby('dt').apply(regression_)
    IC_series = factor_resample.groupby('dt').apply(calcuic)
    group_resdict = groupdiagnosis(n=n, factor_resample=factor_resample.copy())
    return regression_res, IC_series, group_resdict


def longshortyearmonthret(smb=None):
    smbdf = smb.to_frame('ret').reset_index()
    smbdf['y'] = smbdf.dt.dt.year
    smbdf['m'] = smbdf.dt.dt.month
    smbdf.ret = smbdf.ret.fillna(0)
    ymr = smbdf.groupby(['y', 'm']).ret.sum().unstack()
    return ymr


def calcugroupinfo(group_resdict, freq='m'):
    key_value_pairs = group_resdict.keys()
    dfnormalreturn = []
    max_i = max(key_value_pairs)
    min_i = min(key_value_pairs)
    exr = []
    dfreturn = []

    for gp in list(key_value_pairs):
        df_ = group_resdict[gp]

        pr = (df_.exfeereturn.fillna(0) + 1).cumprod()
        br = (df_.benchmark.fillna(0) + 1).cumprod()
        normalreturn = pr / br

        normalreturn.name = gp
        dfnormalreturn.append(normalreturn)

        pr.name = gp
        dfreturn.append(pr)

        Meanturnover = df_.turnoverratio.mean()
        dtm = (pr.index[-1] - pr.index[0]).days / 365
        year_r = 100 * df_.exfeereturn.mean() * freq_dict[freq]
        year_br = 100 * df_.benchmark.mean() * freq_dict[freq]

        exret = year_r - year_br

        yearstd = 100 * df_.exfeereturn.std() * np.sqrt(freq_dict[freq])

        yearsharpe = exret / yearstd
        wr = 100 * (df_.exfeereturn > 0).sum() / df_.exfeereturn.count()
        ex = df_.exfeereturn - df_.benchmark
        wr2 = 100 * (ex > 0).sum() / ex.count()
        exr.append([gp, year_r, exret, yearstd, yearsharpe, wr, wr2, Meanturnover])

    exr = pd.DataFrame(exr,
                       columns=['分组', '年化收益', '超额收益', '年化波动', '夏普比例', '胜率', '超额胜率', '换手率'])

    smb = group_resdict[max_i].exfeereturn - group_resdict[min_i].exfeereturn

    smbr = smb.mean() * freq_dict[freq]

    # dtm = (smb.index[-1] - smb.index[0]).days / 365

    topgp = group_resdict[max_i].exfeereturn - group_resdict[max_i].benchmark

    year_r = 100 * smbr
    yearstd = 100 * smb.std() * np.sqrt(freq_dict[freq])
    smbsharpe = year_r / yearstd
    smbwr = 100 * (smb > 0).sum() / (smb > 0).count()
    longshort = pd.Series([year_r, yearstd, smbsharpe, smbwr, 100 * group_resdict[max_i]['turnoverratio'].mean(),
                           100 * group_resdict[min_i]['turnoverratio'].mean()],
                          index=['多空年化收益', '多空年化波动', '多空夏普比例', '多空胜率', '多头平均换手率',
                                 '空头平均换手率'])
    cumprodr = pd.concat(dfnormalreturn, axis=1)
    dfcumprodr = pd.concat(dfreturn, axis=1)
    smb = 100 * smb
    ymr = longshortyearmonthret(smb=smb)

    smb = pd.concat(
        [group_resdict[max_i].exfeereturn - df_.benchmark, group_resdict[min_i].exfeereturn - df_.benchmark], axis=1)
    smb.columns = ['多头超额收益', '空头超额收益']
    smb['多空超额收益'] = smb['多头超额收益'] - smb['空头超额收益']
    smb = smb * 100

    smb['多头超额累计净值'] = (smb['多头超额收益']).cumsum().fillna(0)
    smb['空头超额累计净值'] = (smb['空头超额收益']).cumsum().fillna(0)
    smb['多空超额累计净值'] = (smb['多空超额收益']).cumsum().fillna(0)
    smb['多空超额最大回撤（%）'] = (100 * (smb['多空超额累计净值'].cummax() - smb['多空超额累计净值']) / smb[
        '多空超额累计净值'].cummax()).replace(np.inf, np.nan).fillna(0)

    return longshort, cumprodr, exr, dfcumprodr, smb, ymr, topgp


def ic_ann(ic_res=None):
    icmean = ic_res.spearman_corr.mean()
    icstd = ic_res.spearman_corr.std()
    icir = icmean / icstd
    icover = (ic_res.spearman_corr > 0).sum() / (ic_res.spearman_corr > 0).count()
    return pd.Series([icmean, icstd, icir, icover], index=['icmean', 'icstd', 'icir', 'icposiratio'])


def regression_ann(regression_res=None):
    abst_mean = abs(regression_res.factor_tvalue).mean()
    t_stat = (regression_res.factor_tvalue > 2).sum() / (regression_res.factor_tvalue > 2).count()
    t_mean = regression_res.factor_tvalue.mean()
    core_mean = regression_res.factor_core.mean()
    return pd.Series([abst_mean, t_stat, t_mean, core_mean], index=['T绝对值平均', 'T大于2比例', 'T均值', '回归系数'])


def plotresults(regression_anares, ic_annres, longshort, IC_series, cumprodr, exr, dfreturn, smb, ymr, name):
    from pyecharts.charts import Bar, Line, Grid, Page, HeatMap
    from pyecharts.components import Table
    from pyecharts import options as opts

    IC_series = round(IC_series, 2)
    bar1 = (
        Bar()
        .add_xaxis(IC_series.index.strftime('%Y-%m-%d').tolist())
        .add_yaxis("柱状图", list(IC_series.spearman_corr), label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(name="IC", name_location="middle", name_gap=30, name_rotate=90),
            legend_opts=opts.LegendOpts(is_show=False, pos_top="8%")
        )
    )

    ic_cumsum = round(IC_series.spearman_corr.cumsum(), 2)

    line1 = (
        Line()
        .add_xaxis(IC_series.index.strftime('%Y-%m-%d').tolist())  # X轴数据为日期，格式化为字符串
        .add_yaxis(
            "IC 累加",
            ic_cumsum.tolist(),
            color='black',  # 线条颜色
            linestyle_opts=opts.LineStyleOpts(width=1)
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="时间", name_location="middle", name_gap=30),
            yaxis_opts=opts.AxisOpts(name="IC 累加", name_location="middle", name_gap=30, name_rotate=90),
            legend_opts=opts.LegendOpts(is_show=False, pos_top="8%", )
        )
    )

    cumprodr = round(cumprodr, 2)

    line2 = (
        Line()
        .add_xaxis(cumprodr.index.strftime('%Y-%m-%d').tolist())  # X轴数据为日期，格式化为字符串

    )
    for column in cumprodr.columns:
        values = cumprodr[column].tolist()
        line2.add_yaxis('%s' % column, values, is_symbol_show=False)

    line2.set_global_opts(
        legend_opts=opts.LegendOpts(is_show=True, pos_bottom="20%", orient='horizontal'),
        xaxis_opts=opts.AxisOpts(type_="time", name="时间", name_location="middle", name_gap=30),
        yaxis_opts=opts.AxisOpts(name="累积收益率(归一化)", name_location="middle", name_gap=30, name_rotate=90),
    )

    dfreturn = round(dfreturn, 2)

    line3 = (
        Line()
        .add_xaxis(dfreturn.index.strftime('%Y-%m-%d').tolist())  # X轴数据为日期，格式化为字符串

    )
    for column in dfreturn.columns:
        values = dfreturn[column].tolist()
        line3.add_yaxis('%s' % column, values, is_symbol_show=False)

    line3.set_global_opts(
        # legend_opts=opts.LegendOpts(is_show=True, pos_top="70%", orient='horizontal'),
        xaxis_opts=opts.AxisOpts(type_="time", name="时间", name_location="middle", name_gap=30),
        yaxis_opts=opts.AxisOpts(name="累积收益率", name_location="middle", name_gap=30, name_rotate=90),
    )

    # line2.add_yaxis(column, values, is_symbol_show=False)

    pse = round(exr['超额收益'], 2)
    bar2 = (
        Bar()
        .add_xaxis(list(pse.index + 1))
        .add_yaxis("柱状图", list(pse), label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(name="分组超额收益", name_location="middle", name_gap=30, name_rotate=90),
            legend_opts=opts.LegendOpts(is_show=False, pos_top="8%")
        )
    )

    exr0 = round(exr, 2)
    # 将 DataFrame 转换为 pyecharts 所需的格式
    table_data = [exr0.columns.tolist()] + exr0.values.tolist()
    table0 = (
        Table()
        .add(headers=exr0.columns.tolist(), rows=exr0.values.tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title="组合")
        )
    )
    # table_html = exr.to_html(index=False, border=0, classes='dataframe', escape=False)
    res_summary = pd.concat([regression_anares,
                             ic_annres,
                             longshort
                             ])

    exr1 = round(res_summary, 3).to_frame("表现情况").reset_index().rename(columns={'index': '名称'})
    # 将 DataFrame 转换为 pyecharts 所需的格式
    table_data = [exr1.columns.tolist()] + exr1.values.tolist()
    table1 = (
        Table()
        .add(headers=exr1.columns.tolist(), rows=exr1.values.tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title="详情")
        )
    )

    ymr = round(ymr, 2)
    min_value = ymr.min().max()
    max_value = ymr.max().max()
    heatmap_data = [(j, i, value) for i, row in enumerate(ymr.values) for j, value in enumerate(row)]
    # 创建热力图

    heatmap = HeatMap()
    heatmap.add_xaxis(ymr.columns.tolist())
    heatmap.add_yaxis("收益", ymr.index.tolist(), heatmap_data)
    heatmap.set_global_opts(title_opts={"text": "多空组合收益(%)"},
                            visualmap_opts=opts.VisualMapOpts(
                                pos_bottom='20%',
                                pos_right='3%',
                                min_=min_value,
                                max_=max_value,
                                is_piecewise=False,  # 连续色带
                            ),
                            yaxis_opts=opts.AxisOpts(name="年度", name_location='center', name_gap=40),
                            xaxis_opts=opts.AxisOpts(name="月份", name_location='center', name_gap=40)

                            )

    heatmap.chart_id = 'heatmap1'

    smb = round(smb, 2)

    line4 = Line()
    line4.add_xaxis(smb.index.strftime('%Y-%m-%d').tolist())
    line4.add_yaxis("空头超额累计净值", smb["空头超额累计净值"].tolist(), linestyle_opts=opts.LineStyleOpts(width=2))
    line4.add_yaxis("多头超额累计净值", smb["多头超额累计净值"].tolist(), linestyle_opts=opts.LineStyleOpts(width=2))
    line4.add_yaxis("多空超额累计净值", smb["多空超额累计净值"].tolist(), linestyle_opts=opts.LineStyleOpts(width=2))

    # 设置右侧 y 轴
    line4.set_global_opts(
        title_opts=opts.TitleOpts(title="净值与回撤曲线"),
        yaxis_opts=opts.AxisOpts(name="净值", name_location='center'),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )

    # 添加右侧 y 轴
    line4.extend_axis(
        yaxis=opts.AxisOpts(name="多空超额最大回撤（%）", position="right", is_inverse=True, name_location='center',
                            name_gap=25)
    )

    line4.add_yaxis("多空超额最大回撤（%）", smb["多空超额最大回撤（%）"].tolist(),
                    areastyle_opts=opts.AreaStyleOpts(opacity=0.5), yaxis_index=1)

    page = Page(layout=Page.DraggablePageLayout)
    bar1.chart_id = 'bar1'
    line1.chart_id = 'line1'
    line2.chart_id = 'line2'
    line3.chart_id = 'line3'
    line4.chart_id = 'line4'
    bar2.chart_id = 'bar2'
    table0.chart_id = 'table0'
    table1.chart_id = 'table1'
    page.add(bar1, line1, line2, line3, bar2, heatmap, line4)
    page.add(table0)
    page.add(table1)
    page.render("render.html")

    Page.save_resize_html("render.html", cfg_file="chart_config (4).json", dest=name)

    # Page.save_resize_html(source="render.html", cfg_file='chart_config (2).json', dest=name1)





