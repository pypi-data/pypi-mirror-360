from functools import singledispatchmethod

import numpy as np
from numba import njit

from numpy import array, arange, full, around, pad, nan_to_num
from numpy import ndarray, dtype
from numpy import int64, nan, int32, float32

from rich.progress import track, Progress
from pathlib import Path

from .base.base_class import CVDFile
from .grid import SeisGrid
from .horiz import Horiz
from .mapping import SEGYMap, TraceField, Trace
import copy


class SeisData(SeisGrid, SEGYMap):
    """"""
    SGY_FIELD = {0: 'time', 1: 'depth', 2: 'depth'}
    SLICE_MIN_LEN = 1

    def __init__(self, sgy_path: Path or str, mode='r', field: int = 0, endian='>'):
        """

        :param sgy_path:
        :param mode:
        :param field: # 0-time(ms), 1-depth(m), 2-depth(ft)
        :param endian:
        """
        SeisGrid.__init__(self, field)
        SEGYMap.__init__(self, sgy_path, endian=endian, mode=mode)

    def getSeiHoriz(self, fill_value=nan):
        cls = Horiz()
        for key in cls.__dict__.keys():
            cls.__setattr__(key, copy.deepcopy(self.__getattribute__(key)))
        names = [self.kINLINE, self.kXLINE, self.kX, self.kY, self.kITRACE, self.kField]
        DType = dtype({'names': names, 'formats': self.ks2fmts(names)})
        cls.initElems(self.shape, DType, fill_value=self.vNAN)
        cls.elems[[*self.dtype.names]] = self.elems[[*self.dtype.names]]
        cls.elems[self.kField] = fill_value
        return cls

    @singledispatchmethod
    def getSlice(self, arg, ijSlice):
        """
        根据不同的索引类型，分派到特定的切片实现函数。
        此方法为默认实现，处理当切片参数k为单个整数时的情况（例如 sgy[..., 1500]）。

        Args:
            arg (int): Z轴（时间/深度）的索引值。
            ijSlice: Inline/Xline维度的切片对象。

        Returns:
            np.ndarray: 一个2D的地震数据切片。
        """
        if isinstance(arg, (int64, int32, int)):
            "k为某一个索引值时,等时/深切片"
            iTraces, state = self.elems[*ijSlice][self.kITRACE], self.bool[*ijSlice]
            data, iTraces = np.empty(iTraces.shape, dtype='f4'), iTraces[state]
            self.traceData([1, 3 - 4], (..., slice(4, 50, 2)))
            data[state], data[~state] = self.traceData(iTraces, [..., arg]), self.vNAN
            # data[state], data[~state] = self._trace[iTraces][Trace.Data.name][..., arg], self.vNAN
            return data
        else:
            raise NotImplementedError("{0}.getSlice haven't being build now!".format(self.__class__.__name__))

    @njit
    @getSlice.register
    def _gs(self, arg: list or tuple or ndarray, ijSlice: list or ndarray or tuple = None):
        """
        处理Z轴为列表、元组或数组时的花式索引情况。
        (例如 sgy[10, 20, [100, 150, 200]])
        注意: 此函数使用了@njit，但内部逻辑包含isinstance(k, Horiz)，
        这在Numba的nopython模式下可能无法按预期工作，可能会回退到object模式。

        Args:
            arg (list | tuple | np.ndarray): Z轴的索引值列表。
            ijSlice: Inline/Xline维度的切片对象。

        Returns:
            np.ndarray: 一个2D的地震数据切片。
        """
        """处理花式索引情况, 索引不含Horiz类"""
        iTraces, state = self.elems[*ijSlice][self.kITRACE], self.bool[*ijSlice]
        state[:] = [k.bool[*ijSlice][n] & state[n] if isinstance(k, Horiz) else state[n] for n, k in enumerate(arg)]
        ks = np.empty(state.shape, dtype=int)
        if hasattr(ijSlice[0], '__iter__') and hasattr(ijSlice[1], '__iter__'):
            """只有花式索引情况"""
            ks[:] = [self.field2k(k.elems[k.kField][*ijSlice])[n] if isinstance(k, Horiz) else k for n, k in
                     enumerate(arg)]
        else:
            """含花式索引及切片情况"""
            ks[:] = [(self.field2k(k.elems[k.kField][*ijSlice])[n] if isinstance(k, Horiz)
                      else (iTraces.size // len(arg)) * [k]) for n, k in enumerate(arg)]
        data, iTraces = np.empty(iTraces.shape, dtype='f4'), iTraces[state]
        data[state], data[~state] = self.traceData(iTraces, [np.arange(len(iTraces)), ks[state]]), self.vNAN
        # data[state], data[~state] = self._trace[iTraces][Trace.Data.name][np.arange(len(iTraces)), ks[state]], self.vNAN
        return data

    @njit
    @getSlice.register
    def _gs(self, arg: Horiz, ijSlice: list or ndarray or tuple = None):
        """
        处理沿单个层位（Horiz对象）进行切片的情况。
        (例如 sgy[..., top_horizon])

        Args:
            arg (Horiz): 用于切片的层位对象。
            ijSlice: Inline/Xline维度的切片对象。

        Returns:
            np.ndarray: 一个2D的、沿层位展平的地震数据切片。
        """
        """k为某一个层位时，沿层位切片, 采用花式索引方式"""
        iTraces, state = self.elems[*ijSlice][self.kITRACE], (arg.bool[*ijSlice] & self.bool[*ijSlice])
        ks = self.field2k(arg.elems[*ijSlice][arg.kField])
        data, iTraces = np.empty(iTraces.shape, dtype='f4'), iTraces[state]
        data[state] = self.traceData(iTraces, [np.arange(iTraces.size), ks[state]]) if len(iTraces) else None
        # data[state] = self._trace[iTraces][Trace.Data.name][np.arange(iTraces.size), ks[state]] if len(iTraces) else None
        data[~state] = self.vNAN
        return data

    @njit
    @getSlice.register
    def _gs(self, arg: slice, ijSlice: list or ndarray or tuple = None):
        """
        处理沿Z轴进行范围切片的情况，支持多种复杂的切片模式。
        (例如 sgy[..., 1000:2000], sgy[..., top:btm], sgy[..., top:top+100])

        Args:
            arg (slice): 切片对象，其 start/stop 属性可以是整数或Horiz对象。
            ijSlice: Inline/Xline维度的切片对象。

        Returns:
            np.ndarray:
                如果start/stop为整数，返回一个3D的地震数据体。
                如果start/stop包含Horiz对象，返回一个2D的对象数组，每个元素是一段地震道数据。
        """
        """层间切片  self.traceData(iTraces, """
        iTraces, state = self.elems[*ijSlice][self.kITRACE], self.bool[*ijSlice]
        shape, hasCls = iTraces.shape, lambda cls, *vs: sum([isinstance(v, cls) for v in vs])
        
        # Case 1: 切片范围的start和stop都不是Horiz对象（即常规的时间/深度切片）
        if hasCls(Horiz, arg.start, arg.stop) == 0:  # 都为Horiz
            data, iTraces = np.empty((*shape, self.smp_seq[arg].size), dtype='f4'), iTraces[state]
            data[state], data[~state] = self.traceData(iTraces, [..., arg]), self.vNAN
            # data[state], data[~state] = self._trace[iTraces][Trace.Data.name][..., arg], self.vNAN
            return data

        # Case 2: 切片范围的start和stop都是Horiz对象（即两层之间的切片）
        if hasCls(Horiz, arg.start, arg.stop) == 2:  # 都为Horiz
            state = arg.stop.bool[*ijSlice] & arg.start.bool[*ijSlice] & state
            starts, stops = self.field2k(
                [arg.start.elems[*ijSlice][arg.start.kField], arg.stop.elems[*ijSlice][arg.stop.kField]])
            data = array(
                [self.traceData(i, [..., slice(start, stop, arg.step)]) if bl else self.vNAN for i, start, stop, bl
                 in zip(iTraces.ravel(), starts.ravel(), stops.ravel(), state.ravel())], dtype=ndarray)
            # data = array([self._trace[i][Trace.Data.name][..., start:stop:arg.step] if bl else self.vNAN for i, start, stop, bl in
            #               zip(iTraces.ravel(), starts.ravel(), stops.ravel(), state.ravel())], dtype=ndarray).reshape(shape)
            data = data.reshape(shape) if np.prod(shape) == data.size else data.reshape(*shape, -1)
            return data
            
        # Case 3: 切片范围的start是Horiz对象, stop是数值
        if hasCls(Horiz, (arg.start, arg.stop, arg.start)) == 2:
            state, starts = arg.start.bool[*ijSlice] & state, self.field2k(arg.start.elems[*ijSlice][self.kField])
            data = array(
                [self.traceData(i, [..., slice(start, arg.stop, arg.step)]) if bl else self.vNAN for i, start, bl in
                 zip(iTraces.ravel(), starts.ravel(), state.ravel())], dtype=ndarray)
            # data = array([self._trace[i][Trace.Data.name][..., start:arg.stop:arg.step] if bl else self.vNAN for i, start, bl in
            #               zip(iTraces.ravel(), starts.ravel(), state.ravel())], dtype=ndarray).reshape(shape)
            data = data.reshape(shape) if np.prod(shape) == data.size else data.reshape(*shape, -1)
            return data

        # Case 4: 切片范围的stop是Horiz对象, start是数值
        if hasCls(Horiz, arg.start, arg.stop, arg.start) == 1:
            state, stops = arg.stop.bool[*ijSlice] & state, self.field2k(arg.stop.elems[*ijSlice][self.kField])
            data = array(
                [self.traceData(i, [..., slice(arg.start, stop, arg.step)]) if bl else self.vNAN for i, stop, bl in
                 zip(iTraces.ravel(), stops.ravel(), state.ravel())], dtype=ndarray)
            # data = array([self._trace[i][Trace.Data.name][..., arg.start:stop:arg.step] if bl else self.vNAN for i, stop, bl in
            #               zip(iTraces.ravel(), stops.ravel(), state.ravel())], dtype=ndarray).reshape(shape)
            data = data.reshape(shape) if np.prod(shape) == data.size else data.reshape(*shape, -1)
            return data

    def __getitem__(self, item):
        """基于getSlice的基础上编写, 主要涉及切片"""
        hasAttr = lambda attr, *vs: sum([hasattr(v, attr) for v in vs])
        if np.isscalar(item) or item is Ellipsis or isinstance(item, slice):
            itraces, state = self.elems[self.kITRACE][item], self.bool[item]
            data = self.traceData(itraces)
            data[~state] = self.vNAN
            return data
        # 检查输入参数是否正确
        if not isinstance(item, tuple) or len(item) > 3 or (item[0] is Ellipsis and len(item) >= 3):
            raise ValueError("index must be tuple, which size is 3.")
        # Ellipsis
        *ij, k = item if len(item) != 2 or item[0] is Ellipsis else (*item, slice(None, None, None))
        # 根据k 的类型获取地震数据
        if isinstance(k, (slice, int32, int64, int, Horiz)):
            """k为非迭代取值情况时"""
            return self.getSlice(k, ijSlice=ij)
        if hasAttr('__iter__', k) and hasAttr('__iter__', *ij) == 0:
            """根据k值切片时"""
            data = np.empty((*self.bool[*ij].shape, len(k)), dtype='f4')
            for i, arg in enumerate(k):
                data[..., i] = self.getSlice(arg, ijSlice=ij)
            return data
        if hasAttr('__iter__', k) and hasAttr('__iter__', *ij) > 0:
            """i, j, k为一维花式索引时"""
            if sum(len(i) != len(k) for i in ij if hasattr(i, '__iter__')):
                raise IndexError("index i, j, k must be same shape!.")
            return self.getSlice(k, ijSlice=ij)

    def load(self):
        """"""
        # 建立
        # self.SetTraceMapping()
        DType = dtype({'names': [self.kINLINE, self.kXLINE, self.kX, self.kY, self.kITRACE],
                       'formats': ['i4', 'i4', 'i4', 'f4', 'i4']})
        dataRows = self.traceHeader(..., TraceField.InlineID, TraceField.XlineID, TraceField.CoordX, TraceField.CoordY,
                                    TraceField.Index).astype(DType)
        # dataRows = np.array(self._trace[Trace.Header.name][[
        #     TraceField.InlineID.name, TraceField.XlineID.name, TraceField.CoordX.name,
        #     TraceField.CoordY.name, TraceField.Index.name]], dtype=DType)
        dataRows[self.kX] = dataRows[self.kX] / self.coord_scale
        dataRows[self.kY] = dataRows[self.kY] / self.coord_scale
        dataRows[self.kITRACE] = np.arange(self.trace_cnt)
        self.setByRows(dataRows)
        return self

    def field2k(self, fieldValue):
        """将层位数据转换成索引矩阵"""
        return nan_to_num(around((fieldValue + array([0]) - self.smp_start) / self.smp_rate, 0), nan=-1).astype(int)

    def iTrace2ij(self, iTrace):
        """将道索引转换成矩阵的索引"""
        lineIDs = self._trace[iTrace][Trace.Header.name][[TraceField.InlineID.name, TraceField.XlineID.name]]
        i, j = self.lineID2ij([lineIDs[TraceField.InlineID.name], lineIDs[TraceField.XlineID.name]])
        return i, j

    def inlineID2iTrace(self, inlineIDs: ndarray or int) -> ndarray or int:
        """"""
        return self.elems[self.kITRACE][self.inlineID2i(inlineIDs)]

    def xlineID2iTrace(self, xlineIDs: ndarray or int) -> ndarray or int:
        """"""
        return self.elems[self.kITRACE][:, self.xlineID2j(xlineIDs)]

    def lineID2iTrace(self, lineIDs: ndarray or int) -> ndarray:
        """"""
        return self.elems[self.kITRACE][self.lineID2ij(lineIDs)]

    def polyline2ij(self, x_coords: ndarray or list, y_coords: ndarray or list):
        """"""
        i, j = self.xy2ij(x_coords, y_coords)
        diff = np.maximum(np.diff(i), np.diff(j))
        toline = lambda n1, n2, l: np.linspace(n1, n2, l + 1)[:-1].round().astype(int)
        iline = [idx for n, length in enumerate(diff) if length > 0 for idx in toline(i[n], i[n + 1], length)]
        jline = [idx for n, length in enumerate(diff) if length > 0 for idx in toline(j[n], j[n + 1], length)]
        return iline, jline


if __name__ == '__main__':
    # 1.地震数据加载及关键字修改
    sgy_path = r"K:\02未整理项目资料\LongDongWork\sgyData\Zhuang8_TWT_Zsm77_SP_0-1_sm2_plan.sgy"

    sgy = SeisData(sgy_path).load()
    from numpy.lib import recfunctions as rfn

    x, y = sgy.fromStructured(sgy.elems[[8, 10, 100], [10, 20, 100]][[sgy.kX, sgy.kY]]).T
    i, j = sgy.polyline2ij(x, y)
    a = np.zeros(sgy.shape, dtype=bool)
    a[i, j] = True
    # 2.地震层位数据加载（目前采用的是segyio库-->给定的单道、道头、数据头读取接口）
    top_path = r"K:\02未整理项目资料\LongDongWork\sgyLayer\Ch71_top.txt"
    btm_path = r"K:\02未整理项目资料\LongDongWork\sgyLayer\Ch73_top.txt"
    # horiz = Horiz.load(horiz_path)

    seisHoriz = sgy.getSeiHoriz(fill_value=1)  # 只加载属于地震数据范围的层位
    top = sgy.getSeiHoriz(fill_value=1).setTimeByTXT(top_path)
    btm = sgy.getSeiHoriz(fill_value=1).setTimeByTXT(btm_path)

    c = sgy[1, 1, top]
    a = sgy[[1, 2, 3], :3, [1, 2, top]]
    b = sgy[[1, 2, 3], [0, 1, 2], [1, 2, top]]

    # 地震数据的获取
    ########################################################################################################################
    # 3.1 获取地震测线数据-->np索引方式(__getitem__实现)，且涉及单道数据切片（层位、索引、时间）
    # CVDFile.SetVDPath()
    a = btm - top
    import matplotlib.pyplot as plt

    ix, iy = sgy.xy2ij([18769117, 4004518])[:]
    area = np.ogrid[-1 + ix:ix + 2:1, iy - 1:iy + 2:1][:]
    sgy.elems[sgy.kINLINE][*np.ogrid[-1 + ix:ix + 2:1, iy - 1:iy + 2:1]]
    sgy.elems[sgy.kXLINE][*np.ogrid[-1 + ix:ix + 2:1, iy - 1:iy + 2:1]]
    d = sgy[*np.ogrid[-1 + ix:ix + 2:1, iy - 1:iy + 2:1][:], :50]
    b = sgy[:, :, [1, 2, top, -1]]
    plt.pcolor(a.elems[a.kX], a.elems[a.kY], b[..., -2])
    plt.show()
    a = sgy[20:50, :50, top]
