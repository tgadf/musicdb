""" AlbumOfTheYear Parsing I/O Class """

__all__ = ["ParseDataIO"]

from dbbase import MusicDBRootDataIO
import dbparse
from dbparse import ParseDataIOBase, ParseFileType
import inspect
from functools import partial
from .params import MusicDBParams
from .rawdataio import RawDataIO


class ParseDataIO(ParseDataIOBase):
    def __repr__(self):
        return f"ParseDataIO(db={self.db})"
    
    def __init__(self, rdio: MusicDBRootDataIO, rawio: RawDataIO, **kwargs):
        super().__init__(rdio, rawio, **kwargs)
        parseMap = MusicDBParams().parseMap
        assert isinstance(parseMap, dict), f"ParseMap [{parseMap}] is not a dict"
        self.parseFuncs = {}

        for parseName, parseType in parseMap.items():
            assert isinstance(parseType, ParseFileType), f'parseName [{parseName}] does not have a ParseFileType'
            parseClassName = getattr(parseType, "parseClassName")
            assert isinstance(parseClassName, str), "No parse class name is set!"
            parseClass = getattr(dbparse, parseClassName)
            assert inspect.isclass(parseClass), f"No parse class with name [{parseClassName}]"
            self.procs[parseName] = parseClass(rdio, rawio, parseType, **kwargs)
            exec(f"self.parse{parseName}Data = partial(self.parse, key='{parseName}')")
            self.parseFuncs[parseName] = getattr(self, f"parse{parseName}Data")