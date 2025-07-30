
from ..singleton_meta import SingletonMeta
from .engine_mon import MonEngine
from .engine_orm import OrmEngine


class DaoEngine(metaclass=SingletonMeta):

    def __init__(self):
        self.mon = MonEngine()
        self.orm = OrmEngine()

