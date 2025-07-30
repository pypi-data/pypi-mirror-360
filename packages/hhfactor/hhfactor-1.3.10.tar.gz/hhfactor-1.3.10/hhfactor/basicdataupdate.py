

import numpy as np
import datetime
import h5py
import os
import pandas as pd
import datetime
import tables as tb
import time
from hhsqllib.sqlconnect import DataBase,get_db
from hhsqllib.sqlfile import database
from hhsqllib.corefunc import corefunc
import warnings
warnings.filterwarnings('ignore')

class BasicDB():

    def __init__(self, stdate = None, localdb = None, sourcedb = None ):
        self.localdb = localdb
        self.sourcedb =  sourcedb
        self.stdate = '20030101' if stdate is None else stdate
        self.funmap = {'eodprice': self.updateeod,
                       'eodindicator': self.updateeodindicator,
                       'tradedate': self.updatetradedate,
                       'indu': self.updateindu,
                       'indexmember': self.updateindexmember,
                       }


    def printnod(self):
        self.factorlibclass = []
        if not os.path.exists(f"{self.localdb}"):
            try:
                print(f"{self.localdb} build h5")
                with tb.open_file(f"{self.localdb}", mode="w") as h5file:
                    pass
            except Exception as e:
                print("Error while build h5", e)
        else:
            with tb.open_file(self.localdb, mode='r') as file:
                for group in file.walk_nodes('/', 'Group'):
                    self.factorlibclass.append(group._v_pathname.replace('/', ''))
                    print(f"Group name: {group._v_pathname}")

    def getdata(self,name):
        with pd.HDFStore(self.localdb, 'a') as store:
            df = store.get(name)
        return df

    def delete_factor_from_h5(self, localdb , factorname = None):
        with h5py.File(localdb, 'r+') as h5file:
            if factorname in h5file:
                del h5file[factorname]
                print(f"表 '{factorname}' 被删除")
            else:
                print(f"表 '{factorname}' 不存在")

    def rebuild(self, name = None):
        if self.check_sheet(name = name ):
            print(f"开始删除表{name}并更新")
            self.delete_factor_from_h5(localdb = self.localdb, factorname=name)
            self.update(name=name)


    def updateall(self):
        for key in self.funmap.keys():
            self.update(name=key)


    def updateeodindicator(self):
        maxdt = self.update_getnewestdate('eodindicator')
        print(f"开始更新 eodindicator 开始日期为 {maxdt}")
        if maxdt != time.strftime('%Y%m%d', time.localtime()):
            dfmv = corefunc.get_eodindicator(dts=maxdt, dte=None, stocklist=None, sourcedb=self.sourcedb)
            dfmv = dfmv[dfmv['dt'] > maxdt]
            self.update_uploaddatabase(name='eodindicator', redf=dfmv)
            print("eodindicator 更新到最新")
        else:
            print("eodindicator 已经是最新")

    def updateeod(self):
        maxdt = self.update_getnewestdate('eodprice')
        print(f"开始更新 eodprice 开始日期为 {maxdt}")
        if maxdt != time.strftime('%Y%m%d', time.localtime()):
            dfeod = corefunc.get_stockeodprice(dts=maxdt, dte=None, stocklist=None, sourcedb=self.sourcedb)
            dfeod = dfeod[dfeod['dt'] > maxdt]
            self.update_uploaddatabase(name='eodprice', redf=dfeod)
            print("eodprice 更新到最新")
        else:
            print("eodprice 已经是最新")

    def update(self, name = 'eodprice'):
        self.funmap[name]()


    def updateindexmember(self):
        print("开始更新 指数成分股信息 ")
        dfindex = corefunc.get_index_members( sourcedb=self.sourcedb)
        self.delete_factor_from_h5(localdb=self.localdb, factorname='indexmember')
        self.update_uploaddatabase(name='indexmember', redf=dfindex)

        # with pd.HDFStore(self.localdb, 'a') as store:
        #     store['indexmember'] = dfindex


    def updatetradedate(self):
        print("开始更新 日期表")
        subsheet =  self.sourcedb.ASHARECALENDAR
        df =  self.sourcedb.query(subsheet.TRADE_DAYS).filter(subsheet.S_INFO_EXCHMARKET == 'SSE').order_by(
            subsheet.TRADE_DAYS).to_df()
        self.delete_factor_from_h5(localdb=self.localdb, factorname='tradedate')
        self.update_uploaddatabase(name='tradedate', redf=df)

        # with pd.HDFStore(self.localdb, 'a') as store:
        #     store['tradedate'] = df

    def updateindu(self):
        print("开始更新 中信一级行业信息 ")
        dfindustry = corefunc.get_industry_all( level=1, sourcedb = self.sourcedb )
        self.delete_factor_from_h5(localdb=self.localdb, factorname='citicindulevelone')
        self.update_uploaddatabase(name='citicindulevelone', redf=dfindustry)
        # with pd.HDFStore(self.localdb, 'a') as store:
        #     store['citicindulevelone'] = dfindustry
        dfindustry = corefunc.get_industry_all( level=2 , sourcedb = self.sourcedb )
        self.delete_factor_from_h5(localdb=self.localdb, factorname='citicinduleveltwo')
        self.update_uploaddatabase(name='citicinduleveltwo', redf=dfindustry)
        # with pd.HDFStore(self.localdb, 'a') as store:
        #     store['citicinduleveltwo'] = dfindustry
        dfindustry = corefunc.get_industry_all(  level=3 ,sourcedb = self.sourcedb )
        self.delete_factor_from_h5(localdb=self.localdb, factorname='citicindulevelthree')
        self.update_uploaddatabase(name='citicindulevelthree', redf=dfindustry)
        # with pd.HDFStore(self.localdb, 'a') as store:
        #     store['citicindulevelthree'] = dfindustry


    def update_uploaddatabase(self, name = None, redf=pd.DataFrame()):
        if redf.empty:
            return None
        else:
            if self.check_sheet(name):
                with pd.HDFStore(self.localdb, 'a') as store:
                    print(f" {len(redf)} {name} 插入数据库")
                    store.append(key=name, value=redf, format='table', chunksize=1000000)
            else:
                columns = list(redf.columns)
                with pd.HDFStore(self.localdb, 'a') as store:
                    print(f" {len(redf)} {name} 插入数据库")
                    store.put(name,  redf, format='table', data_columns=columns)


    def check_sheet(self,name):
        with pd.HDFStore(self.localdb, 'r') as store:
            return name in store

    def update_getnewestdate(self, name = None):
        with pd.HDFStore(self.localdb, 'r') as store:
            if name in store:
                dt_max = store.select(name, columns=['dt'])['dt'].max()
            else:
                dt_max = self.stdate
        return dt_max

    # 返回交易日序列
    def get_trade_dt(self, dts=None, dte=None, offset='first', period='M'):
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
        with pd.HDFStore(self.localdb, 'r') as store:
            df = store.select('tradedate')
        df = df[(df['TRADE_DAYS'] >= dts) & (df['TRADE_DAYS'] <= dte)]
        df['dt'] = pd.to_datetime(df.TRADE_DAYS)
        df.set_index('dt', inplace=True)
        dfresample = df.resample(period)
        tddt = dfresample.agg(offset)
        return tddt[['TRADE_DAYS']]


    def get_citic_indu_levelone(self):
        """

        Returns: 返回中信一级行业

        """
        with pd.HDFStore(self.localdb, 'r') as store:
            df = store.select('citicindulevelone')
        return df[['INDEX_INFO_WINDCODE', 'sid', 'S_CON_INDATE', 'S_CON_OUTDATE',
                   'INDEX_INFO_NAME', 'S_INFO_NAME', 'S_INFO_DELISTDATE',
                   'S_INFO_LISTDATE']]

    def get_eodindicator(self, dts=None, dte=None, sid=None):
        """
        Args:
            dts: 开始时间
            dte: 结束时间
            sid: 股名
        Returns: 返回 eodindicator
        """
        if sid is None:
            with pd.HDFStore(self.localdb, 'r') as store:
                df = store.select('eodindicator', where='dt >= \'%s\' and dt <= \'%s\'' % (dts, dte))
        else:
            with pd.HDFStore(self.localdb, 'r') as store:
                df = store.select('eodindicator',
                                  where='dt >= \'%s\' and dt <= \'%s\' and sid == \'%s\'' % (dts, dte, sid))
        return df


    def get_eodprice(self, dts=None, dte=None, sid=None):
        """

        Args:
            dts: 开始时间
            dte: 结束时间
            sid: 股名
        Returns: 返回 eodpric

        """
        if sid is None:
            with pd.HDFStore(self.localdb, 'r') as store:
                df = store.select('eodprice', where='dt >= \'%s\' and dt <= \'%s\'' % (dts, dte))
        else:
            with pd.HDFStore(self.localdb, 'r') as store:
                df = store.select('eodprice',
                                  where='dt >= \'%s\' and dt <= \'%s\' and sid == \'%s\'' % (dts, dte, sid))
        return df


    def get_indexmember(self,indexcode=None):
        if indexcode is None:
            with pd.HDFStore(self.localdb, 'r') as store:
                df = store.select('indexmember')
        else:
            with pd.HDFStore(self.localdb, 'r') as store:
                df = store.select('indexmember')
                df = df[df['indexcode'] == indexcode]
        return df



if __name__ == '__main__':
    db = database(file=r'D:\FACTOR\sqldatabase.yaml')
    localdb = db.localdb
    sourcedb = get_db(db.sourcedatabase_wind, schem='dbo')
    bdb = BasicDB(localdb=localdb, sourcedb=sourcedb)
    bdb.updateall()





































