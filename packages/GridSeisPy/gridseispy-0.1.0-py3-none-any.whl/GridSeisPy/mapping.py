import ibm2ieee
import numpy as np
from typing import Literal
from pathlib import Path
from enum import Enum
from .base.base_class import CVDFile
from concurrent.futures import ThreadPoolExecutor
import os
import functools


def parallelize_io(min_items_for_parallel=100000):
    """
    一个装饰器，用于将针对长序列的IO操作并行化。
    它会检查被装饰方法的第二个参数(假定为'itrace')的长度，
    如果超过阈值，则使用线程池进行并行处理。
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, itrace, *args, **kwargs):
            # 检查itrace是否为标量或长度小于阈值，如果是，则直接调用原函数
            if np.isscalar(itrace) or len(itrace) < min_items_for_parallel:
                return func(self, itrace, *args, **kwargs)

            # 对于长序列，启用多线程
            max_workers = os.cpu_count() or 1
            chunk_size = (len(itrace) + max_workers - 1) // max_workers
            chunks = [itrace[i:i + chunk_size] for i in range(0, len(itrace), chunk_size)]

            # 使用线程池并行执行原函数
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 每个线程调用的是原始的、未被装饰的函数逻辑
                results = list(executor.map(lambda chunk: func(self, chunk, *args, **kwargs), chunks))

            # 将所有线程返回的numpy数组堆叠成一个
            return np.vstack(results)
        return wrapper
    return decorator


def field_to_dtype(type_field, maxsize: int, endian: str):
    """根据字段获取对应的numpy数据类型"""
    dtype_list = []
    fields = list(type_field)
    for i, field in enumerate(fields):
        # 通过字节位置差值确定数据类型
        byte_size = (fields[i + 1].value if i < len(fields) - 1 else (maxsize + 1)) - field.value
        # dtype = (endian + str(byte_size // 4) + 'i4') if byte_size % 4 == 0 else (endian + str(byte_size // 2) + 'i2')
        num_bytes = byte_size // 4 if byte_size % 4 == 0 else byte_size // 2
        dtype = (endian + 'i4') if byte_size % 4 == 0 else (endian + 'i2')
        dtype_list.append(
            (field.name, dtype, num_bytes) if num_bytes != 1 else (field.name, dtype)  # (名称, 数据类型, 个数)
        )
    return dtype_list


class BinField(Enum):
    """二进制头字段枚举类"""
    k1 = 1
    StartInlineID = 5
    k9 = 9
    k13 = 13
    k15 = 15
    SampleRate = 17     # μs
    k19 = 19
    SamplePoints = 21
    k23 = 23
    DataCode = 25
    k27 = 27
    k29 = 29
    k31 = 31
    k33 = 33
    k35 = 35
    k37 = 37
    k39 = 39
    k41 = 41
    k43 = 43
    k45 = 45
    k47 = 47
    k49 = 49
    k51 = 51
    k53 = 53
    CoordUnit = 55
    k57 = 57
    k59 = 59
    k61 = 61
    StartTime = 63
    Unassigned = 67


class TraceField(Enum):
    """道头字段枚举类"""
    Index = 1
    TraceIndex = 5
    InlineID = 9
    k13 = 13
    k17 = 17
    XlineID = 21
    k25 = 25
    TraceValid = 29
    k31 = 31
    k33 = 33
    k35 = 35
    TraceAngle = 37
    TraceAzimuth = 41
    k45 = 45
    k49 = 49
    k53 = 53
    k57 = 57
    k61 = 61
    k65 = 65
    k69 = 69
    CoordScale = 71
    CoordX = 73
    CoordY = 77
    XRCoord = 81
    YRCoord = 85
    CoordUnit = 89
    k91 = 91
    k93 = 93
    k95 = 95
    k97 = 97
    k99 = 99
    k101 = 101
    k103 = 103
    k105 = 105
    k107 = 107
    k109 = 109
    StartTime = 111
    EndTime = 113
    SamplePoints = 115
    SampleRate = 117
    k119 = 119
    k121 = 121
    k123 = 123
    k125 = 125
    k127 = 127
    k129 = 129
    k131 = 131
    k133 = 133
    k135 = 135
    k137 = 137
    k139 = 139
    k141 = 141
    k143 = 143
    k145 = 145
    k147 = 147
    k149 = 149
    k151 = 151
    k153 = 153
    k155 = 155
    Year = 157
    Day = 159
    Hour = 161
    Minute = 163
    Second = 165
    k167 = 167
    k169 = 169
    k171 = 171
    k173 = 173
    k175 = 175
    k177 = 177
    k179 = 179
    k181 = 181
    k185 = 185
    k189 = 189
    k193 = 193
    k197 = 197
    k201 = 201
    k203 = 203
    k205 = 205
    k209 = 209
    k213 = 213
    k217 = 217
    k219 = 219
    k221 = 221
    k225 = 225
    k229 = 229
    k233 = 233
    k237 = 237


class Trace(Enum):
    Header = TraceField
    Data = None


class SEGYConfig:
    """SEG-Y文件格式配置类"""

    def __init__(self, endian):
        # 默认字节序为大端
        self.endian = endian

        # 文本头配置
        self.text_header_size = 3200
        self.text_header_encoding = 'cp500'     # cp037 、 'cp500'、
        self.binary_header_size = 400
        self.trace_header_size = 240

        # 二进制头和道头配置, 默认是大端顺序进行存储
        self._binary_header_dtype = field_to_dtype(BinField, self.binary_header_size, self.endian)
        self._trace_header_dtype = field_to_dtype(TraceField, self.trace_header_size, self.endian)
        self._trace_data_dtype = f'{self.endian}f4'

    def add_binary_field(self, name, dtype, byte_loc):
        """添加二进制头字段"""
        self._binary_header_dtype.append((name, dtype, byte_loc))

    @property
    def binary_header_dtype(self):
        return np.dtype(self._binary_header_dtype)

    def add_trace_field(self, name, dtype, byte_loc):
        """添加道头字段"""
        self._trace_header_dtype.append((name, dtype, byte_loc))

    @property
    def trace_header_dtype(self):
        return np.dtype(self._trace_header_dtype)

    @property
    def trace_data_dtype(self):
        return np.dtype(self._trace_data_dtype)


_MemMapModeKind = Literal[
    "readonly", "r",
    "copyonwrite", "c",
    "readwrite", "r+",
    "write", "w+",
]


def ieee2ibm32(ieee_binary):
    ieee_binary = ieee_binary
    sign = (ieee_binary >> np.uint32(31)) & np.uint32(0x1)
    exponent = ((ieee_binary >> np.uint32(23)) & np.uint32(0xFF)) - np.uint32(127)
    mantissa = (ieee_binary & np.uint32(0x7FFFFF)) | np.uint32(0x800000)  # 补齐隐含位

    ibm_exponent = (exponent // np.uint32(4)) + np.uint32(64)
    ibm_mantissa = mantissa << (exponent % np.uint32(4))

    ibm_int = (sign << np.uint32(31)) | (ibm_exponent << np.uint32(24)) | (ibm_mantissa & np.uint32(0xFFFFFF))
    return ibm_int

# ieee = np.array([1,2,3,4], dtype='f4')
# # ibm = ieee2ibm32(ieee.view('u4')[:])[:]
# # t = ibm.tobytes(), ibm[0].view('>u4').tobytes()
# ieee.dtype.byteorder
# ibm = np.vectorize(ieee2ibm32)(ieee.view('u4')[:])
# a = ibm2ieee.ibm2float32(ibm.view('u4')[:])[:]
# print()


class SEGYKey(object):
    """"""
    decoder = {
        0: lambda x: x,     # 新建segy数据时，默认用此模式
        1: lambda x: ibm2ieee.ibm2float32(x.view(dtype='>u4')),  # 支持IBM格式数据读取
        5: lambda x: x
    }
    encoder = {
        0: lambda x: x,     # 保存新建的segy数据时，默认用此模式
        1: lambda x: ieee2ibm32(x),    # 目前还没有解决这个问题
        5: lambda x: x,
    }
    d = {
        0: "4-byte IEEE float",     # 保存新建的segy数据时，默认用此模式
        -2: "4-byte native big-endian float",
        -1: "4-byte native little-endian float",
        1: "4-byte IBM float",
        2: "4-byte signed integer",
        3: "2-byte signed integer",
        4: "4-byte fixed point with gain",
        5: "4-byte IEEE float",
        6: "8-byte IEEE float",
        7: "3-byte signed integer",
        8: "1-byte signed char",
        9: "8-byte signed integer",
        10: "4-byte unsigned integer",
        11: "2-byte unsigned integer",
        12: "8-byte unsigned integer",
        15: "3-byte unsigned integer",
        16: "1-byte unsigned char"
    }

    def __init__(self):
        self.floatformat = None
        # 获取基本信息
        self.smp_rate = None    # ms
        self.smp_cnt = None

        # 计算采样序列
        self.smp_start = None
        self.smp_stop = None
        self.smp_seq = None

        # 道数等
        self.trace_cnt = None
        self.coord_scale = None


class SEGYMap(CVDFile, SEGYKey):
    """基于numpy.memmap的SEG-Y文件读取类"""

    def __init__(self, file_path, endian='>', mode: _MemMapModeKind = 'r'):
        CVDFile.__init__(self)
        SEGYKey.__init__(self)
        self.endian = endian
        self.config = SEGYConfig(endian)
        self._file_path = Path(file_path)
        self._mode: _MemMapModeKind = mode
        self._cache_text_header = None
        self._cache_binary_header = None
        self._trace = None
        # 关键信息获取,建立与道的映射关系
        self.ReadKeyInfo()
        self.SetTraceMapping()

    # def CopyNew(self, new_file_path):
    #     """w+模式，会自动创建文件，并以r+模式修改数据
    #     :param new_file_path:
    #     :return:
    #     """
    #     instance: SEGYMap = CVDFile.new(self, self.__class__)
    #     # 创建对应的segy文件
    #     instance._file_path = Path(new_file_path)
    #     instance._mode = 'w+'
    #     # 写入数据
    #     instance.text_header = self.text_header
    #     instance.binary_header = self.binary_header
    #     offset = instance.config.text_header_size + instance.config.binary_header_size
    #     dtype = np.dtype([(Trace.Header.name, instance.config.trace_header_dtype),  # 道头部分
    #                       (Trace.Data.name, self.config.trace_data_dtype, (instance.smp_cnt,))  # 道数据部分
    #                       ])
    #     instance._trace = np.memmap(instance._file_path, dtype=dtype, mode=instance.mode, offset=offset, shape=(instance.trace_cnt,))
    #     a = instance.traceHeader(0, TraceField.CoordScale)
    #     instance.text_header = instance.text_header
    #     instance.binary_header = instance.binary_header
    #     return instance

    @property
    def mode(self) -> _MemMapModeKind:
        if self._mode in ["w+", "write"]:
            open(self._file_path, mode=self._mode).close()
            self._mode: _MemMapModeKind = 'r+'
        return self._mode

    @property
    def text_header(self):
        """
        动态读取, 只能采用该方式得到数据
        :return:
        """
        # 文本头映射
        if self._cache_text_header is None:
            fp = np.memmap(self._file_path, dtype=f'S{self.config.text_header_size}', mode=self.mode, shape=(1,))
            self._cache_text_header = fp.tobytes().decode(self.config.text_header_encoding, errors='ignore')
            del fp  # 删除对象以确保关闭内存映射
        return self._cache_text_header.replace('\0', '')

    @text_header.setter
    def text_header(self, text: str):
        """
        动态更新，只能采用该方式更新数据
        :param text:
        :return:
        """
        if len(text) <= 3200:
            self._cache_text_header = text
            fp = np.memmap(self._file_path, dtype=f'S{self.config.text_header_size}', mode=self.mode, shape=(1,))
            fp[:] = self._cache_text_header.encode(self.config.text_header_encoding)
            fp.flush()
            del fp  # 删除对象以确保关闭内存映射
        else:
            raise IOError('the size of text must be 3200!')

    @property
    def binary_header(self):
        """
        动态读取, 只能采用该方式得到数据
        :return:
        """
        if self._cache_binary_header is None:
            # 二进制头映射
            fp = np.memmap(self._file_path, dtype=self.config.binary_header_dtype, mode=self.mode, offset=self.config.text_header_size, shape=(1,))
            self._cache_binary_header = np.void(fp[0])
            del fp  # 删除对象以确保关闭内存映射
        return self._cache_binary_header

    @binary_header.setter
    def binary_header(self, value):
        """
        动态更新，只能采用该方式更新数据
        :param value:
        :return:
        """
        if value.nbytes == self.config.binary_header_size:
            self._cache_binary_header = value.copy()
            # 二进制头映射
            fp = np.memmap(self._file_path, dtype=self.config.binary_header_dtype, mode=self.mode,
                           offset=self.config.text_header_size, shape=(1,))
            fp[:] = self._cache_binary_header
            fp.flush()
            del fp  # 删除对象以确保关闭内存映射
            self.ReadKeyInfo()  # 更新关键字参数
        else:
            raise IOError(f'the size of value must be {self.config.binary_header_size}!')

    @parallelize_io(min_items_for_parallel=100000)
    def traceData(self, itrace, item=None):
        """
        用接口来读取对应地震数据
        :param itrace:  地震数据读取索引
        :param item: 对读取的地震数据进行切片或者花式索引操作
        :return:
        """
        if item is None:
            return self.decoder[self.floatformat](self._trace[itrace][Trace.Data.name])
        else:
            return self.decoder[self.floatformat](self._trace[itrace][Trace.Data.name][*item])
    
    def SetTraceData(self, itrace, traceData, item=None):
        """

        :param itrace:
        :param traceData:
        :return:
        """
        if self.floatformat == 1:
            self.binary_header[BinField.DataCode.name] = 5
            self.binary_header = self.binary_header
            import warnings
            warnings.warn('雷达encoder中，保存为IBMfloat32格式代码还没写好，暂时以IEEE格式保存')
        if item is None:
            for idx, data in zip(itrace, self.encoder[self.floatformat](traceData)):
                self._trace[idx][Trace.Data.name] = data
        else:
            for idx, data in zip(itrace, self.encoder[self.floatformat](traceData)):
                self._trace[idx][Trace.Data.name][*item] = data
        self._trace.flush()
        return True

    def traceHeader(self, itrace, *keys: TraceField):
        """

        :param itrace:   地震数据读取索引
        :param keys:  枚举类型的关键字
        :return:
        """
        output, ks = lambda ks: self._trace[itrace][Trace.Header.name][ks], ...
        if len(keys) == 0:
            if np.isscalar(itrace):
                return self._trace[itrace][Trace.Header.name]
            return np.array(self._trace[itrace][Trace.Header.name])
        if len(keys) == 1:
            ks = keys[0].name
        if len(keys) > 1:
            ks = [k.name for k in keys]
        if np.isscalar(itrace):
            return output(ks)
        return np.array(output(ks))

    def SetTraceHeader(self, itrace, traceHeader, *keys: TraceField):
        """

        :param itrace:
        :param keys:
        :return:
        """
        if len(keys) == 0:
            for idx, data in zip(itrace, traceHeader):
                self._trace[idx][Trace.Header.name] = data
        else:
            ks = keys[0].name if len(keys) == 1 else [k.name for k in keys]
            for idx, data in zip(itrace, traceHeader):
                self._trace[idx][Trace.Header.name][ks] = data
        self._trace.flush()

    def SetTraceMapping(self, set_trace_cnt: int = 1):
        """
        初始化道数据内存映射
        :param set_trace_cnt: ①创建segy时默认道数为1，读取segy会自动读取对应道数
        :return:
        """
        # 数据区映射
        offset = self.config.text_header_size + self.config.binary_header_size
        dtype = np.dtype([(Trace.Header.name, self.config.trace_header_dtype),  # 道头部分
                          (Trace.Data.name, f'{self.endian}f4', (self.smp_cnt,))  # 道数据部分
                          ])
        # 计算道数
        trace_size = self.config.trace_header_size + self.smp_cnt * 4
        file_trace_cnt = (self._file_path.stat().st_size - (
                    self.config.text_header_size + self.config.binary_header_size)) // trace_size
        self.trace_cnt = max(file_trace_cnt, set_trace_cnt)     #  ①创建segy时默认道数为1，读取segy会自动读取对应道数
        self._trace = np.memmap(self._file_path, dtype=dtype, mode=self.mode, offset=offset, shape=(self.trace_cnt,))
        self.coord_scale = self.traceHeader(0, TraceField.CoordScale)
        # self.coord_scale = 1 if not self.coord_scale else pow(abs(self.coord_scale) + 0.0,  1 if self.coord_scale > 0 else -1)
        self.coord_scale = 1 if not self.coord_scale else abs(self.coord_scale)
        return self

    def ReadKeyInfo(self):
        """读取关键信息"""
        # 地震数据加密格式
        self.floatformat = self.binary_header[BinField.DataCode.name]
        try:
            format_str = 'unknown format!'
            format_str = self.d[self.floatformat]
        except KeyError:
            raise Warning(f"Warning! Unsupported data format: {format_str}, there are may be some problems!")

        # 获取基本信息
        self.smp_rate = self.binary_header[BinField.SampleRate.name] / 1000  # μs to ms
        self.smp_cnt = self.binary_header[BinField.SamplePoints.name]

        # 计算采样序列
        self.smp_start = self.binary_header[BinField.StartTime.name]  # 默认从0开始
        self.smp_stop = float(self.smp_start + (self.smp_cnt - 1) * self.smp_rate)
        self.smp_seq = np.arange(self.smp_start, self.smp_stop + 1, self.smp_rate) if self.smp_start != self.smp_stop else None

    def __len__(self):
        """返回道数"""
        return self.trace_cnt

