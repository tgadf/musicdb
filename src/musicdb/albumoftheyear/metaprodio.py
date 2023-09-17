""" AlbumOfTheYear MetaData IO """

__all__ = ["MetaProducerIO"]

from dbmaster import MasterMetas
from dbmeta import MetaProducerBase
from pandas import concat, DataFrame
from .params import MusicDBParams


class MetaProducerIO(MetaProducerBase):
    def __repr__(self):
        return f"MetaProducerIO(db={self.rdio.db})"
        
    def __init__(self, rdio, **kwargs):
        super().__init__(rdio, **kwargs)
        params = MusicDBParams()
        self.mediaRanking = params.mediaRanking
        if self.verbose:
            print(self.__repr__())
        
        mm = MasterMetas()
        for metaType in mm.getMetaTypes().keys():
            func = f"get{metaType}MetaData"
            if hasattr(self.__class__, func) and callable(getattr(self.__class__, func)) and True:
                self.dbmetas[metaType] = eval(f"self.{func}")
                if self.verbose:
                    print(f"  ==> {metaType}")
    
    ###########################################################################
    # Link MetaData
    ###########################################################################
    def getLinkMetaData(self, modValData):
        assert isinstance(modValData, DataFrame), f"ModValData [{type(modValData)}] is not a DataFrame object"
        cols = ["extra"]
        assert all([col in modValData.columns for col in cols]), f"Could not find all basic columns [{cols}] in DataFrame columns [{modValData.columns}]"
        metaData = []
        
        linkData = modValData[cols].copy(deep=True)
        colData = linkData["extra"].apply(lambda extra: self.getDictData(extra, "RelatedArtists"))
        colData.name = "RelatedArtists"
        metaData.append(colData)
        
        metaData = concat(metaData, axis=1)
        return metaData
    
    ###########################################################################
    # Genre MetaData
    ###########################################################################
    def getGenreMetaData(self, modValData):
        assert isinstance(modValData, DataFrame), f"ModValData [{type(modValData)}] is not a DataFrame object"
        cols = ["genres", "tags"]
        assert all([col in modValData.columns for col in cols]), f"Could not find all basic columns [{cols}] in DataFrame columns [{modValData.columns}]"
        metaData = []
        
        genreData = modValData[cols].copy(deep=True)
        colData = genreData["genres"]
        colData.name = "Genres"
        metaData.append(colData)
        
        colData = genreData["tags"]
        colData.name = "Tags"
        metaData.append(colData)
        
        metaData = concat(metaData, axis=1)
        return metaData

    ###########################################################################
    # Metric MetaData
    ###########################################################################
    def getMetricMetaData(self, modValData):
        assert isinstance(modValData, DataFrame), f"ModValData [{type(modValData)}] is not a DataFrame object"
        cols = ["general"]
        assert all([col in modValData.columns for col in cols]), f"Could not find all basic columns [{cols}] in DataFrame columns [{modValData.columns}]"
        metaData = []
        
        metricData = modValData[cols].copy(deep=True)
        colData = metricData["general"].apply(lambda general: self.getDictData(general, "UserScore"))
        colData.name = "UserScore"
        metaData.append(colData)
        
        colData = metricData["general"].apply(lambda general: self.getDictData(general, "CriticScore"))
        colData.name = "CriticScore"
        metaData.append(colData)
        
        metaData = concat(metaData, axis=1)
        return metaData