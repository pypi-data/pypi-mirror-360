from pathlib import Path
import pickle
import uuid
import numpy as np
import copy
from typing import Type, Any


class ClsManager(type):     # 设置类的变量及方法，区别于实例的变量及方法
    """管理所有类文件存储的原类"""
    __VDFile: Path = None       # 记录类文件的数据表
    __VDFolder: Path = None     # 保存类文件的文件夹
    __ExcludeCls: list = None   # 不加载类

    def __init__(cls, CName, CBases, CAttrs):
        type.__init__(cls, CName, CBases, CAttrs)
        if not hasattr(cls, 'AllCls'):  # 设置类的方法
            cls.__AllCls = {}
        else:
            cls.AddCls(cls)

    @property
    def AllCls(cls):    # 类的方法
        return cls.__AllCls

    def AddCls(cls, newCls):
        clsName = '@'.join([newCls.__module__, newCls.__name__])  # model@class
        cls.__AllCls[clsName] = newCls

    def DelCls(cls, clsName):
        if clsName in cls.__AllCls:
            del cls.__AllCls[clsName]

    def GetCls(cls, clsName=None):
        if clsName is None:
            return cls.__AllCls.values()
        return cls.__AllCls[clsName] if clsName in cls.__AllCls else None

    @staticmethod
    def LoadAllCls():
        """
        根据类定义位置，加载对应的类
        :return:
        """

    def SetVDPath(cls, CVDPath: Path or str = './test.redo', mode='r+') -> None:
        """设置文件地址"""
        if cls.__name__ in ['CVDFile']:
            # 确定 .redo 文件的最终路径
            if isinstance(CVDPath, Path):
                ClsManager.__VDFile = CVDPath.parent / (CVDPath.name + '.redo')
            else:
                ClsManager.__VDFile = Path(CVDPath[:CVDPath.rfind('.')] + '.redo')
            ClsManager.__VDFolder = ClsManager.__VDFile.parent / ClsManager.__VDFile.stem
            if not ClsManager.__VDFolder.exists():
                ClsManager.__VDFolder.mkdir(parents=True, exist_ok=True)
                with ClsManager.__VDFile.open(mode='w', encoding='utf-8') as file:
                    file.write("# redo\n")
                CVDFile._VDFileHex = 0x0
            elif not ClsManager.__VDFile.exists():
                with ClsManager.__VDFile.open(mode='w', encoding='utf-8') as file:
                    file.write("# redo\n")
            else:
                func1 = lambda fileNames: [int(fileName[5:-5], 16) for fileName in fileNames]
                cvdFiles = CVDFile.GetCVDFile()
                CVDFile._VDFileHex = np.max(func1(cvdFiles[..., 3]), axis=0) if len(cvdFiles) != 0 else 0x0

        else:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute 'SetVDPath'")

    def GetVDFolder(cls):
        if cls.__name__ in ['CVDFile']:
            if ClsManager.__VDFile is None:
                raise FileNotFoundError(f"place use the code 'CVDFile.SetVDPath()' to set .redo file, "
                                        f"before you use the code 'Update2VDFile()'")
            return ClsManager.__VDFolder
        else:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute 'GetVDFile'")

    @property
    def VDFile(cls):
        if cls.__name__ in ['CVDFile']:
            if ClsManager.__VDFile is None:
                raise FileNotFoundError(f"place use the code 'CVDFile.SetVDPath()' to set .redo file, "
                                        f"before you 'Update2VDFile()'")
            return ClsManager.__VDFile
        else:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute 'GetVDFile'")

    def GetCVDFile(cls):
        if cls.__name__ in ['CVDFile']:
            converters = lambda line: line.decode().split('=')[-1][1:-1]
            if ClsManager.__VDFile is None:
                raise FileNotFoundError(f"place use the code 'CVDFile.SetVDPath()' to set .redo file, "
                                        f"before you 'Update2VDFile()'")
            cvdFiles = np.loadtxt(str(ClsManager.__VDFile), comments='#', converters=converters, dtype=str).reshape(-1, 4)
            return cvdFiles
        else:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute 'GetVDFile'")

    def GetObjByName(cls, objName):
        """"""
        "clsName  objName    GUID    fileName" "model@class"
        clsName = '@'.join([cls.__module__, cls.__name__])  # model@class
        cvdFiles = CVDFile.GetCVDFile()
        file = cvdFiles[..., 3][(cvdFiles[..., 0] == clsName) & (cvdFiles[..., 1] == objName)]
        if len(file) >= 1:
            path = (ClsManager.__VDFolder / file[0])
            with open(path, 'rb') as file:
                obj = pickle.load(file)
            return obj
        else:
            return None


class CVDFile(metaclass=ClsManager):
    _VDFileHex: int = None  # 当前可分配文件编号

    def __init__(self):
        # CVDFile.__VDFileHex = 5
        self._VDFileHex = CVDFile._VDFileHex
        CVDFile._VDFileHex = None if CVDFile._VDFileHex is None else CVDFile._VDFileHex + 1
        pass

    @property
    def fileHex(self): return None if self._VDFileHex is None else f'file{self._VDFileHex:04x}.lmx'

    def Update2VDFile(self, objName: str = None):
        """
        更新文件, 保存文件名称不变，内容改变
        :param objName:
        :return:
        """
        xmlFile = CVDFile.GetVDFolder() / f'file{self._VDFileHex:04x}.lmx'
        uuid5 = uuid.uuid5(uuid.NAMESPACE_DNS, str(xmlFile))
        clsName = '@'.join([self.__module__, self.__class__.__name__])
        cvdFiles = CVDFile.GetCVDFile()
        file_idx = np.where(cvdFiles[..., 2] == str(uuid5))[0]
        if sum(file_idx) == 0:    # 未保存类数据，保存二进制文件，并更新文件索引
            with open(CVDFile.VDFile, 'a') as f:
                f.write(f"clsName='{clsName}'  objName='{objName}'  GUID='{uuid5}'    fileName='{xmlFile.name}'\n")
        else:
            import warnings
            warnings.warn('如果file_idx有多个，即存在多个实例指向同一个文件的处理方法，还没写！', UserWarning)
        with open(xmlFile, 'wb') as file:
            pickle.dump(self, file)

    def __deepcopy__(self, memo):
        """"""
        new_instance = self.__class__.__new__(self.__class__)
        memo[id(self)] = new_instance  # 止循环引用
        for key, value in self.__dict__.items():
            setattr(new_instance, key, copy.deepcopy(value, memo))
        new_instance._VDFileHex = CVDFile._VDFileHex
        CVDFile._VDFileHex = None if CVDFile._VDFileHex is None else CVDFile._VDFileHex + 1
        return new_instance

    def new(self, cls: Type[Any]):
        """
        从实例中，获取类的参数, 不会赋值带_ 和 __的属性（仅内部使用和私有属性）
        :param cls:
        :return:
        """
        # 创建cls的实例
        instance = cls.__new__(cls)
        # 深拷贝self的属性到新实例
        for key, value in self.__dict__.items():
            setattr(instance, key, copy.deepcopy(getattr(self, key)))
        # 返回新实例
        return instance


# class test(CVDFile):
#     """"""
#
#     def __init__(self):
#         CVDFile.__init__(self)
#         pass
#
#     def HHH(self):
#         pass
#
#
# class test2(CVDFile):
#     """"""
#     def __init__(self):
#         CVDFile.__init__(self)
#         pass
#
#     def HHH(self):
#         pass
#
# CVDFile.SetVDPath()
# a = test()
# g = test()
# c = test2()
# a.hhh = np.linspace(1, 500)
# a.Update2VDFile()
# a.Update2VDFile('b')
# a.Update2VDFile('c')
# a.Update2VDFile('b')
#
# b = test.GetObjByName('a')
# hh = test()
# CVDFile.AllCls
# CVDFile.VDFile
# test.VDFile
# test2.AllCls
# a.AllCls
# print(b.hhh)
#
# # 类方法
# CVDFile.SetVDPath()
# CVDFile.VDPath
# CVDFile.VDFolder
# CVDFile.VDFile

