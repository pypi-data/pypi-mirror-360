import datetime

import pandas as pd
import numpy as np

from pandarallel import pandarallel
# pandarallel.initialize(progress_bar=False, nb_workers=8)

class calcucore:




    @staticmethod
    def getlastannreportperiod(dt=None):
        """
        Args:
            dt: %Y%m%d format eg '20240101'

        Returns:
            the newest ann financial report ,
        """
        dti = pd.to_datetime(dt)
        monthi = dti.month
        year = dti.year
        if 5 <= monthi:
            return '%d1231' % (year - 1)
        else:
            return '%d1231' % (year - 2)



    @staticmethod
    def getyearreportlastfiveyearslist(dt = None):
        """
        Args:
            dt: %Y%m%d format eg '20240101'

        Returns:
            the last five year financial reports ,
        """
        dti = pd.to_datetime(dt)
        monthi = dti.month
        year = dti.year
        if 1 <= monthi <= 4:
            yearend = year - 1
        else:
            yearend = year
        years = np.arange(yearend - 6, yearend,1)
        f = lambda x : "%d1231"%x
        return list(map(f ,years))



    @staticmethod
    def getlastyearreportperiod(dt = None):
        """
        Args:
            dt: %Y%m%d format eg '20240101'

        Returns:
            the newest financial report ,
        """
        dti = pd.to_datetime(dt)
        monthi = dti.month
        year = dti.year
        if 1 <= monthi <= 4:
            return '%d0930' % (year - 1)
        elif 5 <= monthi <= 8:
            return '%d1231' % (year - 1)
        elif 9 <= monthi <= 10:
            return '%d0630' % year
        elif 11 <= monthi <= 12:
            return '%d0930' % year
        else:
            return np.NAN

    @staticmethod
    def getlastyearreportperiodmrq(dt = None):
        """
                Args:
                    dt: %Y%m%d format eg '20240101'

                Returns:
                    the newest financial report ,
                """
        dti = pd.to_datetime(dt)
        monthi = dti.month
        year = dti.year
        if 1 <= monthi <= 4:
            return '%d0930' % (year - 1)
        elif 5 <= monthi <= 8:
            return '%d0331' % (year)
        elif 9 <= monthi <= 10:
            return '%d0630' % year
        elif 11 <= monthi <= 12:
            return '%d0930' % year
        else:
            return np.NAN





    @staticmethod
    def middeextre(seri, multiplier=5):
        x_M = np.median(seri)
        x_MAD = np.median(np.abs(seri - x_M))
        upper = x_M + multiplier * x_MAD
        lower = x_M - multiplier * x_MAD
        seri[seri > upper] = upper
        seri[seri < lower] = lower
        return seri

    @staticmethod
    def normalize(x):
        return  ((x - np.mean(x))/np.std(x))

    @staticmethod
    def get_exp_weight(window, half_life):
        exp_wt = np.asarray([0.5 ** (1 / half_life)] * window) ** np.arange(window)
        return exp_wt[::-1]/np.sum(exp_wt)