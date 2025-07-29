from pathlib import Path
from typing import Literal
import time
import os

from ..Bbasic import B_Color

COLOR_DICT = {
    "default": B_Color.RESET,

    "black": B_Color.BLACK,
    "red": B_Color.RED,
    "green": B_Color.GREEN,
    "yellow": B_Color.YELLOW,
    "blue": B_Color.BLUE,
    "purple": B_Color.PURPLE,
    "cyan": B_Color.CYAN,
    "silver": B_Color.SILVER
}
Color_Literal = Literal["default", "black", "red", "green", "yellow", "blue", "purple", "cyan", "silver"]

class B_Writer:
    def __init__(
            self,
            path: Path,
            ifTime: bool = False,
            color: Color_Literal = 'default',
    ):
        '''
        :param path: 日志保存路径
        :param ifTime: 是否输出时间
        '''
        super().__init__()
        self.path = Path(path)
        self.ifTime = ifTime
        self.toWant_file = False
        self.toWant_cmd = False

        self.__checkColor(color)
        self.color = color

        self.f = None
        self.setFile(self.path, self.ifTime)

    def setFile(self, file: Path, ifTime=False):
        '''
        设置 file的path 以及 writer的ifTime
        :param file: 设置log路径
        :param ifTime:
        :return:
        '''
        if self.f is not None:
            self.f.close()
        self.path = Path(file)
        self.ifTime = ifTime
        self.__createDir(self.path)
        self.f = open(self.path, "a", encoding="utf-8")

    def clearFile(self):
        '''
        清空内容
        '''
        assert self.f is not None, "请先调用setFile方法"
        self.f.close()
        self.f = open(self.path, 'w', encoding="utf-8")

    def closeFile(self):
        '''
        关闭log
        '''
        if self.f:
            self.f.close()
            self.f = None

    def toCmd(self, string, color: Color_Literal = None):
        '''
        打印到terminal
        '''
        # 检查color是否在字典中
        if color is None:
            print(COLOR_DICT.get(self.color) + str(string) + B_Color.RESET)
        else:
            assert color in COLOR_DICT, f"color参数错误，请输入{COLOR_DICT.keys()}"
            print(COLOR_DICT.get(color) + str(string) + B_Color.RESET)

    def toFile(self, string, ifTime=None):
        '''
        写入到文件内
        '''
        assert self.f is not None, "请先调用setFile方法"

        if ifTime == False:
            pass
        elif ifTime==True or self.ifTime==True:
            t = time.strftime("%Y-%m-%d %H:%M:%S ##### ", time.localtime())
            self.f.write(t)

        self.f.write(str(string))
        self.f.write("\n")
        self.f.flush()

    def toBoth(self, string, ifTime=False, color: Color_Literal = None):
        '''
        同时写入到文件和terminal
        :param string:
        :param color:
        :return:
        '''
        self.toFile(str(string), ifTime)
        self.toCmd(str(string), color)

    def setWant(self, toCmd=False, toFile=False):
        '''
        toWant的全局选项设置
        '''
        self.toWant_cmd = toCmd
        self.toWant_file = toFile

    def toWant(self, string, ifTime=False, color: Color_Literal = None):
        '''
        使用前先调用setWant方法
        '''
        if self.toWant_cmd and self.toWant_file:
            self.toBoth(string, ifTime, color)
        elif self.toWant_cmd:
            self.toCmd(string, color)
        elif self.toWant_file:
            self.toFile(string, ifTime)
        else:
            raise Exception("请先调用setWant方法, 设置toCmd或toFile为True")

    def __checkColor(self, color):
        assert color in COLOR_DICT, f"color参数错误，请输入{list(COLOR_DICT.keys())}"

    def __createDir(self, path):
        # 获取到该文件的文件夹
        dir = path.parents[0]
        os.makedirs(dir, exist_ok=True)