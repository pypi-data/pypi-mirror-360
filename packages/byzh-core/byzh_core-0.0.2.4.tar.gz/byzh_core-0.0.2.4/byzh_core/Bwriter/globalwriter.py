import threading
import time
import atexit


class B_GlobalWriter():
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # 初始化
                    cls._instance.file = None
                    cls._instance.f = None
                    cls._instance.ifTime = False
                    atexit.register(cls._instance.closeFile)  # 注册关闭方法
        return cls._instance

    @classmethod
    def setFile(cls, file, ifTime=False):
        cls()
        cls._instance.ifTime = ifTime
        cls._instance.path = file
        cls._instance.f = open(cls._instance.path, "a", encoding="utf-8")

    @classmethod
    def clearFile(cls):
        cls()
        assert cls._instance.f is not None, "请先调用setFile方法"
        cls._instance.f.close()
        cls._instance.f = open(cls._instance.path, 'w', encoding="utf-8")

    @classmethod
    def closeFile(cls):
        if cls._instance.f:
            cls._instance.f.close()
            cls._instance.f = None

    @classmethod
    def toCmd(cls, string):
        cls()
        print(string)

    @classmethod
    def toFile(cls, string):
        cls()
        assert cls._instance.f is not None, "请先调用setFile方法"
        if  cls._instance.ifTime:
            t = time.strftime("%Y-%m-%d %H:%M:%S ##### ", time.localtime())
            cls._instance.f.write(t)
        cls._instance.f.write(string)
        cls._instance.f.write("\n")
        cls._instance.f.flush()

    @classmethod
    def toBoth(cls, string):
        cls()
        cls.toFile(string)
        cls.toCmd(string)
