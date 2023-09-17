""" AlbumOfTheYear Merging I/O Class """

__all__ = ["MergeDataIO"]

from dbbase import MusicDBRootDataIO
from dbparse import MergeDataIOBase, MergeFileType
from functools import partial
from .params import MusicDBParams
from .rawdataio import RawDataIO


class MergeDataIO(MergeDataIOBase):
    def __repr__(self):
        return f"MergeDataIO(db={self.db})"
    
    def __init__(self, rdio: MusicDBRootDataIO, rawio: RawDataIO, **kwargs):
        super().__init__(rdio, **kwargs)
        mergeMap = MusicDBParams().mergeMap
        assert isinstance(mergeMap, dict), f"MergeMap [{mergeMap}] is not a dict"
        self.mergeData = partial(self.merge, key=None)
        self.mergeFuncs = {}

        for mergeName, mergeType in mergeMap.items():
            if mergeName == "ModVal" and isinstance(mergeType, dict):
                self.procs[mergeName] = eval("MergeModValDataIO(mdbdata, mdbdir, mergeType, **kwargs)")
                exec(f"self.merge{mergeName}Data = partial(self.merge, key='ModVal')")
            elif isinstance(mergeType, MergeFileType):
                self.procs[mergeName] = eval(f"Merge{mergeType.inputType}DataIO(mdbdata, mdbdir, mergeType, **kwargs)")
                exec(f"self.merge{mergeName}Data = partial(self.merge, key='{mergeName}')")
            self.mergeFuncs[mergeName] = getattr(self, f"merge{mergeName}Data")