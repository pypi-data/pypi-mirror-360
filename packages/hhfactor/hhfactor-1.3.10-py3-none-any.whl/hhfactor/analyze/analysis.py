import matplotlib.pyplot as plt
import pandas as pd
from ..factor import Factor
from hhsqllib.corefunc import corefunc
from hhsqllib.sqlfile import database
from hhsqllib.sqlconnect import get_db
from ..algor.factortreatment import *
from ..algor.datetreatment import *

def factoranalysis(factorname='bplf_regression', freq='m', dbo=None, factor0=None, indexcode='000906.SH', ifkeep=True,
                   dts='20100101', dte='20250701'):
    factor0.dropna(inplace=True)
    factor_resample = factor_addindumv(factor=factor0.copy(), freq=freq, dts=dts, dte=dte, dbo=dbo,
                                       offset='last')

    factor_resample = factor_clean(factor_resample=factor_resample, method='drop', ifkeep=ifkeep)
    regression_res, IC_series, group_resdict = factordiagnosis(n=10, factor_resample=factor_resample)

    dtlist = list(
        map(lambda x: pd.to_datetime(step_trade_dt(dt_handle(x), 1), format='%Y%m%d'), list(regression_res.index)))

    regression_res.index = dtlist
    regression_res.index.name = 'dt'
    IC_series.index = dtlist
    IC_series.index.name = 'dt'

    ic_annres = ic_ann(ic_res=IC_series)

    ymic = longshortyearmonthret(smb=IC_series.spearman_corr)

    regression_anares = regression_ann(regression_res=regression_res)

    longshort, cumprodr, exr, dfreturn, smb, ymr, topgp = calcugroupinfo(group_resdict, freq=freq)

    ic_annres['factor'] = factorname
    ic_annres['stockpool'] = 'total'

    with pd.ExcelWriter('.\\results\\%s-%s.xlsx' % (indexcode, factorname)) as writer:
        regression_res.to_excel(writer, sheet_name='%s-回归系数' % indexcode, index=True)
        regression_anares.to_excel(writer, sheet_name='%s-回归分析' % indexcode, index=True)
        IC_series.to_excel(writer, sheet_name='%s-IC序列' % indexcode, index=True)
        ic_annres.to_excel(writer, sheet_name='%s-IC分析' % indexcode, index=True)
        ymic.to_excel(writer, sheet_name='%s-IC年度月度表现' % indexcode, index=True)
        longshort.to_excel(writer, sheet_name='%s-多空组合表现' % indexcode, index=True)
        exr.to_excel(writer, sheet_name='%s-每一组收益分析' % indexcode, index=True)
        cumprodr.to_excel(writer, sheet_name='%s-组合累计收益(归一化)' % indexcode, index=True)
        dfreturn.to_excel(writer, sheet_name='%s-组合累计收益(原始)' % indexcode, index=True)
        smb.to_excel(writer, sheet_name='%s-多空表现' % indexcode, index=True)
        ymr.to_excel(writer, sheet_name='%s-多空组合年度月度表现' % indexcode, index=True)
        topgp.to_excel(writer, sheet_name='%s-多头组合超额' % indexcode, index=True)

#
#
#
# factorname = 'bplf_regression'
# freq = 'm'
# db = database(file=r'D:\FACTOR\sqldatabase.yaml')
# sourcedb = get_db(db.sourcedatabase_wind, schem='dbo')
# l1 = Factor(stdate=None, localdb=db.localdb, sourcedb=sourcedb, freq='Monthly')
# factordf = l1.getdata_byfactor(factorname=factorname)
# factor0 = factordf.copy()
# #中证800
# indexcode = '000906.SH'
#
# indexstockpool = indexmemberseries(indexcode=[indexcode], dbo = sourcedb )
# factor0 = indexstockpool.merge(factor0, on=['sid', 'dt'], how='left')
# factor0 = factor0[['dt', 'sid', 'indexcode', 'factor_value']]
# coverseries = coverratiodescripe(factor0)
# factor0.dropna(inplace=True)
# factor_resample = factor_addindumv(factor=factor0.copy(), freq=freq, dts = '20100101', dte = '20250331' , dbo=  l1 , offset='last')
# factor_resample = factor_clean(factor_resample=factor_resample, method='drop', ifkeep=False)
# regression_res, IC_series, group_resdict = factordiagnosis(n=10, factor_resample=factor_resample)
# ic_annres = ic_ann(ic_res=IC_series)
# ymic = longshortyearmonthret(smb = IC_series.spearman_corr)
# regression_anares = regression_ann(regression_res=regression_res)
# longshort,cumprodr,exr,dfreturn,smb,ymr,topgp = calcugroupinfo(group_resdict, freq=freq)
#
#
#
# ic_annres['factor'] = factorname
# ic_annres['stockpool'] = 'total'
#
# with pd.ExcelWriter('.\\results\\%s.xlsx'%factorname) as writer:
#     coverseries.to_excel(writer, sheet_name='%s-因子覆盖度水平'%indexcode, index=True)
#     regression_res.to_excel(writer, sheet_name='%s-回归系数'%indexcode, index=True)
#     regression_anares.to_excel(writer, sheet_name='%s-回归分析'%indexcode, index=True)
#     IC_series.to_excel(writer, sheet_name='%s-IC序列'%indexcode, index=True)
#     ic_annres.to_excel(writer, sheet_name='%s-IC分析'%indexcode, index=True)
#     ymic.to_excel(writer, sheet_name='%s-IC年度月度表现'%indexcode, index=True)
#     longshort.to_excel(writer, sheet_name='%s-多空组合表现'%indexcode, index=True)
#     exr.to_excel(writer, sheet_name='%s-每一组收益分析'%indexcode, index=True)
#     cumprodr.to_excel(writer, sheet_name='%s-组合累计收益(归一化)' % indexcode, index=True)
#     dfreturn.to_excel(writer, sheet_name='%s-组合累计收益(原始)' % indexcode, index=True)
#     smb.to_excel(writer, sheet_name='%s-多空表现'%indexcode, index=True)
#     ymr.to_excel(writer, sheet_name='%s-多空组合年度月度表现'%indexcode, index=True)
#     topgp.to_excel(writer, sheet_name='%s-多头组合超额'%indexcode, index=True)