""" Primary AlbumOfTheYear Music DB I/O Container """

__all__ = ["MusicDBIO"]

from dbbase import MusicDBIOBase
from dbmeta import SummaryProducerIO, MatchProducerIO
from dbparse import MusicDBGroupDataIO
from .params import MusicDBParams
from .rawdataio import RawDataIO
from .musicdbid import MusicDBID
from .parseio import ParseDataIO
from .concatio import ConcatDataIO
from .mergeio import MergeDataIO
from .metaprodio import MetaProducerIO
from .mediasumprodio import MediaSummaryProducerIO
from .matchomit import MatchOmit

    
###############################################################################
# Music DB I/O Container
###############################################################################
class MusicDBIO(MusicDBIOBase):
    def __repr__(self):
        return f"MusicDBIO(db={self.db})"
        
    def __init__(self, **kwargs):
        self.params = MusicDBParams()
        super().__init__(db=self.params.db, **kwargs)
        self.gdio = MusicDBGroupDataIO(self.rdio, self.params, **kwargs)
        self.gdio.addGroupData()
        self.gdio.addSearchData("SearchArtist", "aotyArtistsData")
        omit = MatchOmit(**kwargs)
        
        #######################################################################
        # I/O
        #######################################################################
        self.rawio = RawDataIO()
        self.mdbid = MusicDBID()
        self.getdbid = self.mdbid.get
        self.pdio = ParseDataIO(self.rdio, self.rawio, **kwargs)
        self.mdio = MergeDataIO(self.rdio, self.rawio, **kwargs)
        self.cdio = ConcatDataIO(self.rdio, self.rawio, **kwargs)
        self.metaprodio = MetaProducerIO(self.rdio, **kwargs)
        self.sumprodio = SummaryProducerIO(self.rdio, **kwargs)
        self.medsumprodio = MediaSummaryProducerIO(self.rdio, **kwargs)
        self.matchprodio = MatchProducerIO(self.rdio, omit, **kwargs)
        