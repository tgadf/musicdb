""" AlbumOfTheYear Concating I/O Class """

__all__ = ["ConcatDataIO"]

from dbbase import MusicDBRootDataIO
import dbparse
from dbparse import ConcatDataIOBase, ConcatFileType
from functools import partial
import inspect
from .params import MusicDBParams
from .rawdataio import RawDataIO


class ConcatDataIO(ConcatDataIOBase):
    def __repr__(self):
        return f"ConcatDataIO(db={self.db})"
        
    def __init__(self, rdio: MusicDBRootDataIO, rawio: RawDataIO, **kwargs):
        super().__init__(rdio, **kwargs)
        concatMap = MusicDBParams().concatMap
        assert isinstance(concatMap, dict), f"ConcatMap [{concatMap}] is not a dict"
        self.concatData = partial(self.concat, key=None)
        self.concatFuncs = {}
        
        for concatName, concatType in concatMap.items():
            if concatName == "ModVal" and isinstance(concatType, dict):
                concatCls = getattr(dbparse, "ConcatModValDataIO")
            elif isinstance(concatType, ConcatFileType):
                concatCls = getattr(dbparse, concatType.concatClassName)
            else:
                raise TypeError(f"Unknown concat type: {concatName} => {concatType}")
            assert inspect.isclass(concatCls), f"concat class [{concatCls}] is not a class"
            self.procs[concatName] = concatCls(rdio, concatType, **kwargs)
            exec(f"self.concat{concatName}Data = partial(self.concat, key='{concatName}')")
            self.concatFuncs[concatName] = getattr(self, f"concat{concatName}Data")