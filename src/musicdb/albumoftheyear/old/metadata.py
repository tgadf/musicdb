""" DB-specific Metadata """

__all__ = ["MetaData"]

from meta import MetaDataBase, MediaTypeRankBase, MetaDataUtilsBase, MediaMetaData, UniversalMetaData
from pandas import DataFrame
from listUtils import getFlatList
from timeutils import Timestat

from .musicdbid import MusicDBID
from .rawdbdata import RawDBData


#####################################################################################################################################
# Base DB MetaData
#####################################################################################################################################
class MetaData(MetaDataBase):
    def __init__(self, mdbdata, **kwargs):
        super().__init__(mdbdata, **kwargs)
        self.utils = AlbumOfTheYearMetaDataUtils()
        self.umd   = UniversalMetaData()
        self.mmd   = MediaMetaData(MediaTypeRank())

        if self.verbose: print("{0} ModValMetaData".format(self.db))
        self.dbmetas = {}
        for meta in self.mdbdata.metas:
            func = "get{0}MetaData".format(meta)
            if hasattr(self.umd.__class__, func) and callable(getattr(self.umd.__class__, func)):
                self.dbmetas[meta] = eval("self.umd.{0}".format(func))
                if self.verbose: print("  ==> {0} (Universal)".format(meta))
            elif hasattr(self.mmd.__class__, func) and callable(getattr(self.mmd.__class__, func)):
                self.dbmetas[meta] = eval("self.mmd.{0}".format(func))
                if self.verbose: print("  ==> {0} (Media)".format(meta))
            elif hasattr(self.__class__, func) and callable(getattr(self.__class__, func)):
                self.dbmetas[meta] = eval("self.{0}".format(func))
                if self.verbose: print("  ==> {0}".format(meta))
                
        
    def make(self, modVal=None, metatype=None):
        modVals = self.getModVals(modVal)
        if self.verbose: ts = Timestat("Making {0} {1} MetaData".format(len(modVals), self.db))
        
        for i,modVal in enumerate(modVals):            
            if (i+1) % 25 == 0 or (i+1) == 5:
                if self.verbose: ts.update(n=i+1, N=len(modVals))
            modValData = self.mdbdata.getModValData(modVal)

            metas = {meta: metaFunc for meta,metaFunc in self.dbmetas.items() if ((isinstance(metatype,str) and meta == metatype) or (metatype is None))}
            for meta,metaFunc in metas.items():
                if self.verbose: print("  ==> {0} ... ".format(meta), end="")
                metaData = metaFunc(modValData)
                if self.verbose: print("{0}".format(metaData.shape))
                eval("self.mdbdata.saveMeta{0}Data".format(meta))(modval=modVal, data=metaData)                        
                    
        if self.verbose: ts.stop()

            
    ###############################################################################################################
    # Link MetaData
    ###############################################################################################################
    def getLinkMetaData(self, modValData):
        relatedArtists = modValData.apply(self.utils.getRelatedArtists)
        relatedArtists.name = "RelatedArtists"
           
        relatedArtists = modValData.apply(self.utils.getMediaArtistNames)
        relatedArtists.name = "MediaArtists"
           
        pageRefs = modValData.apply(self.utils.getPageRefs)
        pageRefs.name = "PageRefs"
           
        metaData = DataFrame(relatedArtists)
        return metaData

            
    ###############################################################################################################
    # Genre MetaData
    ###############################################################################################################
    def getGenreMetaData(self, modValData):
        artistGenres = modValData.apply(self.utils.getGenres)
        artistGenres.name = "Genre"
           
        artistTags = modValData.apply(self.utils.getTags)
        artistTags.name = "Tag"
           
        metaData = DataFrame([artistGenres,artistTags]).T
        return metaData

            
    ###############################################################################################################
    # Genre MetaData
    ###############################################################################################################
    def getMetricMetaData(self, modValData):
        artistCriticScore = modValData.apply(self.utils.getCriticScore)
        artistCriticScore.name = "CriticScore"
           
        artistUserScore = modValData.apply(self.utils.getUserScore)
        artistUserScore.name = "UserScore"
           
        metaData = DataFrame([artistCriticScore,artistUserScore]).T
        return metaData
        
    

#####################################################################################################################################
# Media Type Rank  Utils
#####################################################################################################################################
class MediaTypeRank(MediaTypeRankBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mediaRanking['A'] = ['LP', "Compilation", "Box Set"]
        self.mediaRanking['B'] = ['Single', "EP"]
        self.mediaRanking['C'] = ['Cover']
        self.mediaRanking['D'] = ['Score', 'Soundtrack', 'Instrumental']
        self.mediaRanking['E'] = ['Mixtape', 'Remix', 'DJ Mix']
        self.mediaRanking['F'] = ['Live', 'Unofficial']
        self.mediaRanking['G'] = ['Video']
        
        

#####################################################################################################################################
# Base DB MetaData
#####################################################################################################################################
class AlbumOfTheYearMetaDataUtils(MetaDataUtilsBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mdbid   = MusicDBID()


    ############################################################# Genre #############################################################
    def getGenres(self, rData):
        genresData = self.getGenresData(rData)
        retval = [item.text for item in genresData] if isinstance(genresData,list) else None
        return retval

    def getTags(self, rData):
        tagsData = self.getTagsData(rData)
        retval = [item.text for item in tagsData] if isinstance(tagsData,list) else None
        return retval

    
    ############################################################# Link #############################################################
    def getRelatedArtists(self, rData):
        relatedArtists = self.getExtraData(rData, 'RelatedArtists')
        retval = {self.mdbid.get(item.href): (item.href, item.text) for item in relatedArtists} if isinstance(relatedArtists,list) else None
        return retval
    
    def getMediaArtistNames(self, rData):
        mediaArtists = getFlatList([artist for artist in self.getMediaArtists(rData) if isinstance(artist,list)])        
        retval = {self.mdbid.get(item.href): (item.href, item.text) for item in mediaArtists} if isinstance(mediaArtists,list) else None
        return retval

    def getPageRefs(self, rData):
        pageRefs = self.getExtraData(rData, 'PageRefs')
        retval = {self.mdbid.get(item.href): (item.href, item.text) for item in pageRefs} if isinstance(pageRefs,list) else None
        return retval
    

    ############################################################# Metric #############################################################
    def getUserScore(self, rData):
        score = self.getGeneralData(rData, "UserScore")
        return score

    def getCriticScore(self, rData):
        score = self.getGeneralData(rData, "CriticScore")
        return score