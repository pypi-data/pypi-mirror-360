from numpy import nan
from .settings import DefaultSetting


class SeisKeys(DefaultSetting):
    """关键字全部小写"""

    # MD, TVD, SSTVD, TWT = ['md', 'tvd', 'sstvd', 'twt']
    # INLINE, XLINE, X, Y = ['inline', 'xline', 'x', 'y']
    # ITRACE, TIME, DEPTH = ['itrace', 'time', 'depth']
    # INVVAL_S, INVVAL_V, NAN = ['-999.25', -999.25, nan]
    # FORMATS = {'i4': [INLINE, XLINE, ITRACE], 'f4': [MD, TVD, SSTVD, TWT, X, Y, TIME, DEPTH]}

    def __init__(self, field):
        self.__kMD, self.__kTVD, self.__kSSTVD, self.__kTWT = ['md', 'tvd', 'sstvd', 'twt']  # 关键字k
        self.__kINLINE, self.__kXLINE, self.__kX, self.__kY = ['inline', 'xline', 'x', 'y']  # 关键字ij
        self.__kField, self.__kITRACE, self.__kTIME, self.__kDEPTH = [field, 'itrace', 'time', 'depth']  # filed
        self.__vINV, self.__sINV, self.__vNAN = [-999.25, '-999.25', nan]
        self.__format = {'i4': [self.kINLINE, self.kXLINE, self.kITRACE],
                         'f4': [self.kMD, self.kTVD, self.kSSTVD, self.kTWT, self.kX, self.kY, self.kTIME, self.kDEPTH],}

    def ks2fmts(self, keys):
        """keys to formats"""
        dtype = ['O'] * len(keys)
        for i, k in enumerate(keys):
            for item in self.__format.items():
                if k in item[1]:
                    dtype[i] = item[0]
        return dtype

    @property
    def vINV(self): return self.__vINV

    @property
    def sINV(self): return self.__sINV

    @property
    def vNAN(self): return self.__vNAN

    @property
    def kMD(self): return self.__kMD

    @property
    def kTVD(self): return self.__kTVD

    @property
    def kSSTVD(self): return self.__kSSTVD

    @property
    def kTWT(self): return self.__kTWT

    @property
    def kINLINE(self): return self.__kINLINE

    @property
    def kXLINE(self): return self.__kXLINE

    @property
    def kX(self): return self.__kX

    @property
    def kY(self): return self.__kY

    @property
    def kITRACE(self): return self.__kITRACE

    @property
    def kTIME(self): return self.__kTIME

    @property
    def kDEPTH(self): return self.__kDEPTH

    @property
    def kField(self): return self.kDEPTH if self.__kField else self.kTIME
