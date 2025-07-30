import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 将项目根目录添加到 Python 路径，以便导入 seispy
project_root = Path(__file__).resolve().parent.parent.parents[0]
sys.path.append(str(project_root))
print(project_root)
from seispy import SeisData, Horiz


def main():
    """
    一个演示如何使用 seispy 库加载和处理地震数据的示例。
    """  
    # --- 1. 定义文件路径 ---
    # 请注意：您需要将以下路径替换为您本地 SGY 和层位文件的实际路径才能运行此示例。
    # 为了演示，我们假设路径存在。在实际运行中，如果文件不存在，程序会报错。
    sgy_path =  r"G:\02未整理项目资料\LongDongWork\sgyData\Zhuang8_TWT_Zsm77_SP_0-1_sm2_plan.sgy"
    top_path = r"G:\02未整理项目资料\LongDongWork\sgyLayer\Ch71_top.txt"
    btm_path = r"G:\02未整理项目资料\LongDongWork\sgyLayer\Ch73_top.txt"

    print(f"尝试加载SGY文件: {sgy_path}")
    print(f"尝试加载层位文件: {top_path}, {btm_path}")
    print("-" * 30)

    # --- 2. 加载数据 ---
    try:
        # 加载SGY数据
        sgy = SeisData(sgy_path, mode='r').load()
        print(f"SGY文件加载成功。")
        print(f"  - 地震数据维度 (inlines, xlines, samples): {sgy.shape}")
        print(f"  - 时间/深度范围: {sgy.smp_start}ms to {sgy.smp_stop}ms")
        print(f"  - 采样率: {sgy.smp_rate / 1000}ms") # 转换为毫秒
        print("-" * 30)

        # 加载层位数据
        # 首先创建一个与地震数据网格匹配的空层位对象
        top_horiz = sgy.getSeiHoriz().setTimeByTXT(top_path, skiprows=2)
        btm_horiz = sgy.getSeiHoriz().setTimeByTXT(btm_path, skiprows=2)
        print("层位文件加载成功。")
        print("-" * 30)

    except Exception as e:
        print(f"错误：加载文件时发生错误。")
        print(f"请检查文件路径是否正确，以及文件格式是否符合要求。")
        print(f"原始错误: {e}")
        # 创建一个假的演示数据以便后续代码可以执行
        print("\n注意：由于找不到文件，正在创建虚拟数据进行演示...")
        sgy = create_dummy_seis_data()
        top_horiz, btm_horiz = create_dummy_horizons(sgy)
        print("虚拟数据创建成功。")
        print("-" * 30)


    # --- 3. 数据切片与提取 ---
    print("演示数据切片操作:")

    # 3.1 沿剖面切片
    inline_slice = sgy.getInline(sgy.arrInlines[sgy.shape[0] // 2])
    xline_slice = sgy.getXline(sgy.arrXlines[sgy.shape[1] // 2])
    print(f"  - 提取了第 {sgy.shape[0] // 2} 条 Inline, 维度: {inline_slice.shape}")
    print(f"  - 提取了第 {sgy.shape[1] // 2} 条 Xline, 维度: {xline_slice.shape}")

    # 3.2 沿层位切片
    slice_along_top = sgy[..., top_horiz]
    print(f"  - 沿顶层位切片, 维度: {slice_along_top.shape}")

    # 3.3 提取两层之间的地震数据
    data_between_horizons = sgy[..., top_horiz:btm_horiz]
    print(f"  - 提取两层之间的地震数据, 这是一个不规则对象数组, 维度: {data_between_horizons.shape}")
    print("-" * 30)

    # --- 4. 可视化 ---
    print("正在生成可视化图像...")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("SeisPy 功能演示")

    # 绘制 Inline
    axes[0].imshow(inline_slice.T, cmap='seismic', aspect='auto')
    axes[0].set_title(f"Inline {sgy.arrInlines[sgy.shape[0] // 2]}")
    axes[0].set_xlabel("Xline Index")
    axes[0].set_ylabel("Time Sample")


    # 绘制沿层位切片
    axes[1].imshow(slice_along_top, cmap='viridis', aspect='auto')
    axes[1].set_title("Slice Along Top Horizon")
    axes[1].set_xlabel("Xline Index")
    axes[1].set_ylabel("Inline Index")

    # 绘制一个位置的道数据
    trace_data = data_between_horizons[data_between_horizons.shape[0]//2, data_between_horizons.shape[1]//2]
    axes[2].plot(trace_data, np.arange(len(trace_data)))
    axes[2].set_title("Trace Between Horizons")
    axes[2].set_xlabel("Amplitude")
    axes[2].set_ylabel("Time Sample (relative)")
    axes[2].invert_yaxis()


    plt.tight_layout()
    plt.show()
    print("示例执行完毕。")


def create_dummy_seis_data():
    """创建一个虚拟的 SeisData 对象用于演示"""
    # 模拟一个 SeisData 对象需要的属性
    class DummySGY(SeisData):
        def __init__(self):
            self.shape = (100, 100, 250)
            self.smp_start = 1000
            self.smp_stop = 2000
            self.smp_rate = 4000  # 4ms, in microseconds
            self.arrInlines = np.arange(100, 200)
            self.arrXlines = np.arange(500, 600)
            self._data = np.random.rand(100, 100, 250) * 2 - 1

        def load(self):
            return self

        def getSeiHoriz(self):
            h = Horiz()
            h.initElems(self.shape[:2], dtype=np.dtype([('time', 'f4')]))
            return h

        def getInline(self, iline_val):
            idx = np.where(self.arrInlines == iline_val)[0][0]
            return self._data[idx, :, :]

        def getXline(self, xline_val):
            idx = np.where(self.arrXlines == xline_val)[0][0]
            return self._data[:, idx, :]

        def __getitem__(self, item):
            # 简化版 __getitem__
            i_slice, j_slice, k_slice = item
            if isinstance(k_slice, Horiz):
                # 模拟沿层切片
                k_indices = np.clip(k_slice.elems['time'], 0, self.shape[2]-1).astype(int)
                return self._data[i_slice, j_slice, k_indices]
            elif isinstance(k_slice, slice) and isinstance(k_slice.start, Horiz) and isinstance(k_slice.stop, Horiz):
                # 模拟层间切片 (返回对象数组)
                data = np.empty(self.shape[:2], dtype=object)
                start_indices = np.clip(k_slice.start.elems['time'], 0, self.shape[2]-1).astype(int)
                stop_indices = np.clip(k_slice.stop.elems['time'], 0, self.shape[2]-1).astype(int)
                for i in range(self.shape[0]):
                    for j in range(self.shape[1]):
                        start, stop = min(start_indices[i,j], stop_indices[i,j]), max(start_indices[i,j], stop_indices[i,j])
                        data[i, j] = self._data[i, j, start:stop]
                return data
            return self._data[item]

    return DummySGY()


def create_dummy_horizons(sgy):
    """为虚拟地震数据创建虚拟层位"""
    top_h = sgy.getSeiHoriz()
    x = np.linspace(0, 2*np.pi, sgy.shape[1])
    y = np.linspace(0, 2*np.pi, sgy.shape[0])
    xx, yy = np.meshgrid(x, y)
    z_top = (np.sin(xx) + np.cos(yy) + 2) * 40 + 50 # 模拟起伏的层位
    top_h.elems['time'] = z_top.astype(int)

    btm_h = sgy.getSeiHoriz()
    z_btm = z_top + 50 # 模拟一个平行的地层
    btm_h.elems['time'] = z_btm.astype(int)

    return top_h, btm_h


if __name__ == '__main__':
    main()


