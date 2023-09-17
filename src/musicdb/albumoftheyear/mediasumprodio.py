""" AlbumOfTheYear Media Summary Data IO """

__all__ = ["MediaSummaryProducerIO"]

from dbbase import MusicDBRootDataIO
from dbmeta import MediaSummaryProducerBase
from utils import Timestat, getFlatList
from pandas import DataFrame, Series

        
class MediaSummaryProducerIO(MediaSummaryProducerBase):
    def __repr__(self):
        return f"MediaSummaryProducerIO(db={self.db})"
        
    def __init__(self, rdio: MusicDBRootDataIO, **kwargs):
        super().__init__(rdio, **kwargs)
        if self.verbose:
            print(self.__repr__())
            
        #######################################################################
        # (Artist) Media Data Info
        #######################################################################
        self.addMediaInfo("Album", ["genres", "userscore", "criticscore", "pagerefs", "year"])
        self.addArtistMediaInfo("ArtistMedia", ["mediaID", "year"])
        self.setArtistIDPos(0)
        
        #######################################################################
        # Processes To Run
        #######################################################################
        for summaryType in self.summaryTypes.keys():
            func = "makeMedia{0}SummaryData".format(summaryType)
            if hasattr(self.__class__, func) and callable(getattr(self.__class__, func)):
                self.procs[summaryType] = eval(f"self.{func}")
                if self.verbose:
                    print("  ==> {0}".format(summaryType))
        
    ###########################################################################
    # Artist ID => Media Dates Map
    ###########################################################################
    def makeMediaDatesSummaryData(self, **kwargs):
        summaryType = "Dates"
        ts = Timestat(f"Making {self.db} Media {summaryType} Summary Data", verbose=self.verbose)
            
        # Data
        df = self.getJoinedMediaData("ArtistMedia", "Album", ["year"])
        df = df[df["year"].notna()]
        numArtists = df["ArtistID"].nunique()
        
        # Grouping
        if self.verbose:
            ts.update(cmt=f"  Grouping [{df.shape[0]}] {summaryType} Data For {numArtists} Unique Artists (will take a minute) ... ")
        summaryData = df[["ArtistID", "year"]].groupby(["ArtistID"]).apply(lambda x: x["year"].describe())
        summaryData.index.name = None
        summaryData.columns.name = None
        
        # Joining
        basicData = self.rdio.getData("SummaryNumAlbums")
        ts.update(cmt=f"  Joining [{summaryData.shape[0]}] {summaryType} Data With All [{basicData.shape[0]}] Summary IDs  ... ")
        summaryData = DataFrame(basicData).join(summaryData).drop(["NumAlbums"], axis=1)

        if self.verbose is True:
            print(f"  ==> Created {summaryData.shape[0]} Artist ID => Name {summaryType} Summary Data")

        if self.test is True:
            print("  ==> Only testing. Will not save.")
        else:
            self.rdio.saveData("SummaryDates", data=summaryData)
        
        ts.stop()
            
    ###########################################################################
    # Artist ID => Genre Map
    ###########################################################################
    def makeMediaGenreSummaryData(self, **kwargs):
        summaryType = "Genre"
        ts = Timestat(f"Making {self.db} Media {summaryType} Summary Data", verbose=self.verbose)
            
        def getGenres(df):
            genres = df["genres"]
            if len(genres) == 0:
                return None
            genres = getFlatList([value for value in genres.values if isinstance(value, list)])
            if len(genres) == 0:
                return None
            genres = Series(genres, dtype='object')
            retval = genres.value_counts().head(3).index.to_list()
            return retval
        
        # Data
        df = self.getJoinedMediaData("ArtistMedia", "Album", ["genres"])
        df = df[df["genres"].notna()]
        numArtists = df["ArtistID"].nunique()
        colName = "MediaGenres"
        
        # Grouping
        ts.update(cmt=f"  Grouping [{df.shape[0]}] {summaryType} Data For {numArtists} Unique Artists (will take a minute) ... ")
        summaryData = df[["ArtistID", "genres"]].groupby(["ArtistID"]).apply(getGenres)
        summaryData.index.name = None
        summaryData.name = colName

        if self.verbose is True:
            print(f"  ==> Created {summaryData.shape[0]} Artist ID => Name {summaryType} Summary Data")

        if self.test is True:
            print("  ==> Only testing. Will not save.")
        else:
            self.joinSummaryData(summaryType, summaryData, ts, saveit=True)
        
        ts.stop()
            
    ###########################################################################
    # Artist ID => Link Map
    ###########################################################################
    def makeMediaLinkSummaryData(self, **kwargs):
        summaryType = "Link"
        ts = Timestat(f"Making {self.db} Media {summaryType} Summary Data", verbose=self.verbose)
            
        def getPageRefs(df):
            pageRefs = df["pagerefs"]
            pageRefs = pageRefs[pageRefs.apply(lambda x: isinstance(x, list))]
            retval = {artistID: {"Name": artistName, "URL": artistRef} for artistPageRefs in pageRefs.values for (artistID, artistName, artistRef) in artistPageRefs}
            retval = None if len(retval) == 0 else retval
            return retval
        
        # Data
        df = self.getJoinedMediaData("ArtistMedia", "Album", ["pagerefs"])
        df = df[df["pagerefs"].notna()]
        numArtists = df["ArtistID"].nunique()
        colName = "MediaPageRefs"
        
        # Grouping
        ts.update(cmt=f"  Grouping [{df.shape[0]}] {summaryType} Data For {numArtists} Unique Artists (will take a minute) ... ")
        summaryData = df[["ArtistID", "pagerefs"]].groupby(["ArtistID"]).apply(getPageRefs)
        summaryData.index.name = None
        summaryData.name = colName

        if self.verbose is True:
            print(f"  ==> Created {summaryData.shape[0]} Artist ID => Name {summaryType} Summary Data")

        if self.test is True:
            print("  ==> Only testing. Will not save.")
        else:
            self.joinSummaryData(summaryType, summaryData, ts, saveit=True)
        
        ts.stop()
        
    ###########################################################################
    # Artist ID => Media Metric Map
    ###########################################################################
    def makeMediaMetricSummaryData(self, **kwargs):
        summaryType = "Metric"
        ts = Timestat(f"Making {self.db} Media {summaryType} Summary Data", verbose=self.verbose)
            
        # Data
        df = self.getJoinedMediaData("ArtistMedia", "Album", ["userscore", "criticscore"])
        df = df[((df["userscore"].notna()) | (df["criticscore"].notna()))]
        numArtists = df["ArtistID"].nunique()
        colName = ["MediaUserScore", "MediaCriticScore"]
        
        # Grouping
        ts.update(cmt=f"  Grouping [{df.shape[0]}] {summaryType} Data For {numArtists} Unique Artists (will take a minute) ... ")
        summaryData = df[["ArtistID", "userscore", "criticscore"]].groupby(["ArtistID"]).apply(lambda x: [x["userscore"].max(), x["criticscore"].max()])
        summaryData = summaryData.apply(Series)
        summaryData.index.name = None
        summaryData.columns = colName

        if self.verbose is True:
            print(f"  ==> Created {summaryData.shape[0]} Artist ID => Name {summaryType} Summary Data")

        if self.test is True:
            print("  ==> Only testing. Will not save.")
        else:
            self.joinSummaryData(summaryType, summaryData, ts, saveit=True)
        
        ts.stop()
        