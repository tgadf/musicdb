""" Container Class For DBIDs To Omit From Match """

__all__ = ["MatchOmit"]

from dbmeta import MatchOmitBase
from .params import MusicDBParams


###############################################################################
# Container Class For DBIDs To Omit From Match
###############################################################################
class MatchOmit(MatchOmitBase):
    def __repr__(self):
        return f"MatchOmit(db={self.db})"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        params = MusicDBParams()
        omitData = {dbid: True for dbid in params.omit.values()}
        nOmit = len(omitData)
        self.setOmitData(omitData)
        self.db = params.db
        
        if self.verbose is True:
            print(f"{self.__repr__()}: {nOmit} IDs To Omit From Match")
            