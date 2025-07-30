import pandas as pd
import numpy as np
import datetime
import h5py
import os
import pandas as pd
import numpy as np
import datetime
import tables as tb
from hhsqllib.sqlconnect import DataBase, get_db
from hhfactor.algor.factoralgo import factortool
from hhfactor.algor.datetreatment import *


class Factor(factortool):
    def __init__(self, name=None, stdate='20040101', eddate=None, localdb=None, sourcedb=None, freq='Daily'):
        self.name = None
        self.stdate = None
        self.eddate = None
        self.localdb = None
        self.sourcedb = None
        self.factorvalue = None
        self.freq = freq
        self.init(name=name, stdate=stdate, eddate=eddate, localdb=localdb, sourcedb=sourcedb)

    def init(self, name=None, stdate=None, eddate=None, localdb=None, sourcedb=None):
        self.name = name
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name
        self.stdate = '20100101' if stdate is None else stdate
        self.eddate = datetime.datetime.now().strftime("%Y%m%d") if eddate is None else eddate
        self.localdb = localdb
        self.sourcedb = sourcedb
        self.localfile = localdb
        self.factorvalue = None
        self.freqfunc = eval(self.freq)(-1)

        if not os.path.exists(f"{self.localdb}"):
            try:
                print(f"{self.localdb} build h5")
                with tb.open_file(f"{self.localdb}", mode="w") as h5file:
                    pass
            except Exception as e:
                print("Error while build h5", e)
        assert os.path.exists(f"{self.localfile}"), "the localdb not exist"
        self.factorlibclass = []
        with tb.open_file(localdb, mode='r') as file:
            # 遍历整个文件中的所有 Group 节点
            for group in file.walk_nodes('/', 'Group'):
                if group._v_pathname != '/':
                    self.factorlibclass.append(group._v_pathname.replace('/', ''))

    def rebuild_factor(self, redf=None):
        self.check_dataframe_columns(df=redf)
        Factor.delete_factor_from_h5(self.localdb, factorname=self.name)
        self.buildsheet_factorsheet()
        self.update_uploaddatabase(redf=redf)

    def check_sheet(self):
        with pd.HDFStore(self.localfile, 'r') as store:
            isin_ = self.name in store
        return isin_

    def update_getnewestdate(self):
        with pd.HDFStore(self.localfile, 'r') as store:
            if self.name in store:
                df = store[self.name].dropna(subset='dt')
                if df.empty:
                    dt_max = self.stdate
                else:
                    dt_max = df['dt'].max()

            else:
                dt_max = self.stdate
        return dt_max

    def update_calcufactor(self):
        dt_max = self.update_getnewestdate()
        if dt_max is None:
            dt_max = self.stdate
        factor_calcu = getattr(self, 'get_factor_value')
        print(f"计算因子 {self.name}")
        if dt_max >= self.eddate:
            print(f"当前因子表已经更新到最新 {dt_max}")
            self.factorvalue = pd.DataFrame()
            return None

        self.stdate = max(step_trade_dt(dt_max, -252), '20100101')

        trade_dt_list = self.freqfunc.get(self.stdate, self.eddate).tolist()

        if len(trade_dt_list) == 0:
            print(f"当前因子表已经更新到最新 {dt_max}")
            self.factorvalue = pd.DataFrame()
            return None
        df = factor_calcu()
        df = df[df['dt'] > dt_max]
        self.update_uploaddatabase(redf=df)
        print(f"{self.name} 因子更新完成")
        return None

    def update_all(self):
        if self.check_sheet():
            Factor.delete_factor_from_h5(localfile=self.localfile, factorname=self.name)
            self.buildsheet_factorsheet()
            factor_calcu = getattr(self, 'updateall')
            print(f"开始更新{self.name} 开始时间为 {self.stdate} ，结束时间为{self.eddate} ")
            rel = factor_calcu()
            rel.replace(np.nan, None, inplace=True)
            self.update_uploaddatabase(rel)

        else:
            self.buildsheet_factorsheet()
            factor_calcu = getattr(self, 'updateall')
            print(f"开始更新{self.name} 开始时间为 {self.stdate} ，结束时间为{self.eddate} ")
            rel = factor_calcu()
            rel.replace(np.nan, None, inplace=True)
            self.update_uploaddatabase(rel)

    def update_uploaddatabase(self, redf=pd.DataFrame()):
        if redf.empty:
            return None
        else:
            redf['opdt'] = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
            redf['factor_value'] = redf['factor_value'].astype(float)
            print(redf)
            with pd.HDFStore(self.localfile, 'a') as store:
                print(f" {len(redf)} {self.name} 插入数据库")
                try:
                    store.append(key=self.name, value=redf, format='table', chunksize=1000000)
                except Exception as e:
                    print(e)
                finally:
                    if store is not None:
                        store.close()

    def update(self):
        if self.check_sheet():
            self.update_calcufactor()
        else:
            self.buildsheet_factorsheet()
            self.update_calcufactor()

    def buildsheet_factorsheet(self):
        print(f"建表 {self.name} 因子")
        try:
            with pd.HDFStore(self.localfile, 'a') as store:
                df = pd.DataFrame([[None, None, None, None]], columns=['sid', 'dt', 'factor_value', 'opdt'])
                df['factor_value'] = df['factor_value'].astype(float)
                # df.to_hdf(self.localfile, self.name,format = 'table')
                store.put(key=self.name, value=df, format='table', data_columns=True,
                          min_itemsize={'sid': 20, 'dt': 20, 'factor_value': 20, 'opdt': 20})
            print(f"完成建表 {self.name} 因子")
        except Exception as e:
            print("Error while storing DataFrame:", e)

    def getdata_bystock(self, sid=None):
        with pd.HDFStore(self.localfile, 'r') as store:
            if self.name in store:
                df = store[self.name]
                return df[df['sid'] == sid]
            else:
                return pd.DataFrame()

    def getdata_bydt(self, dt=None):
        with pd.HDFStore(self.localfile, 'r') as store:
            if self.name in store:
                df = store[self.name]
                return df[df['dt'] == dt]
            else:
                return pd.DataFrame()

    def getdata_bystockdt(self, dt=None, sid=None):
        with pd.HDFStore(self.localfile, 'r') as store:
            if self.name in store:
                df = store[self.name]
                return df[(df['dt'] == dt) & (df['sid'] == sid)]
            else:
                return pd.DataFrame()

    def printnod(self, todata='myfactorlib.txt'):
        self.factorlibclassdict = {}
        if not os.path.exists(f"{self.localfile}"):
            try:
                print(f"{self.localfile} build h5")
                with tb.open_file(f"{self.localfile}", mode="w") as h5file:
                    pass
            except Exception as e:
                print("Error while build h5", e)
        else:
            with tb.open_file(self.localfile, mode='r') as file:
                for group in file.walk_nodes('/', 'Group'):
                    if group._v_pathname != '/':
                        self.factorlibclassdict[group._v_pathname.replace('/', '')] = group['table'].colnames
                    print(f"Group name: {group._v_pathname}")
        if todata is None:
            pass
        else:
            with open(todata, 'w') as f:
                for idx, (key, value) in enumerate(self.factorlibclassdict.items(), start=1):
                    f.write(f"{idx}. {key}: {value}\n")

    def getdata_bysiddt(self, sid=None, dt=None, factorname=None, columns=None):
        if factorname is None:
            dftotal = pd.DataFrame()
            for name in self.factorlibclass:
                with pd.HDFStore(self.localfile, 'r') as store:
                    df = store.select(name, where='sid == \'%s\' and dt == \'%s\'' % (sid, dt), columns=columns)
                    df['factorname'] = name
                    dftotal = dftotal._append(df)
            return dftotal
        else:
            with pd.HDFStore(self.localfile, 'r') as store:
                df = store.select(factorname, where='sid == \'%s\' and dt == \'%s\'' % (sid, dt), columns=columns)
                df['factorname'] = factorname
                return df

    def getdata_bydt(self, dt=None, factorname=None, columns=None):
        if factorname is None:
            dftotal = pd.DataFrame()
            for name in self.factorlibclass:
                with pd.HDFStore(self.localfile, 'r') as store:
                    df = store.select(name, where='dt == \'%s\'' % dt, columns=columns)
                    df['factorname'] = name
                    dftotal = dftotal._append(df)
            return dftotal
        else:
            with pd.HDFStore(self.localfile, 'r') as store:
                df = store.select(factorname, where='dt == \'%s\'' % dt, columns=columns)
                df['factorname'] = factorname
                return df

    def getdata(self, sid=None, factorname=None, dt=None, columns=None):
        if sid is None and dt is not None:
            dftotal = self.getdata_bydt(dt=dt, factorname=factorname, columns=columns)
        elif dt is None and sid is not None:
            dftotal = self.getdata_bysid(sid=sid, factorname=factorname, columns=columns)
        elif sid is not None and dt is not None:
            dftotal = self.getdata_bysiddt(sid=sid, dt=dt, factorname=factorname, columns=columns)
        elif sid is None and dt is None:
            dftotal = self.getdata_byfactor(factorname=factorname, columns=columns)
        else:
            dftotal = pd.DataFrame()
        return dftotal

    def getdata_byfactor(self, factorname=None, columns=None):
        with pd.HDFStore(self.localfile, 'r') as store:
            df = store.select(factorname, columns=columns)
            df['factorname'] = factorname
            return df

    def getdata_bysid(self, sid=None, factorname=None, columns=None):
        if factorname is None:
            dftotal = pd.DataFrame()
            for name in self.factorlibclass:
                with pd.HDFStore(self.localfile, 'r') as store:
                    df = store.select(name, where='sid == \'%s\'' % sid, columns=columns)
                    df['factorname'] = name
                    dftotal = dftotal._append(df)
            return dftotal
        else:
            with pd.HDFStore(self.localfile, 'r') as store:
                df = store.select(factorname, where='sid == \'%s\'' % sid, columns=columns)
                df['factorname'] = factorname
                return df

    def check_dataframe_columns(self, df=None):
        required_columns = {'sid', 'dt', 'factor_value'}
        df_columns = set(df.columns)
        # 使用 assert 来检查列是否匹配
        assert df_columns == required_columns, f"DataFrame 的列不符合要求，缺少列或有额外列。当前列: {df_columns}, 需要的列: {required_columns}"

    @staticmethod
    def delete_factor_from_h5(localfile, factorname=None):
        with h5py.File(localfile, 'r+') as h5file:
            if factorname in h5file:
                del h5file[factorname]
                print(f"表 '{factorname}' 被删除")
            else:
                print(f"表 '{factorname}' 不存在")

# fc = Factor()
# fc.init( name='test1', stdate='20240101', eddate='20240105', localfile='factordata.h5')
# fc.check_sheet()
# fc.buildsheet_factorsheet()
# self = fc
# with pd.HDFStore(self.localfile, 'r') as store:
#     print(store.keys())
#     print(store['test1'])
#     print(store[dataset_name])



