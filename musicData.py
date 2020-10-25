from sys import prefix
from os import getcwd
from os.path import join
from pandas import concat
from ioUtils import getFile, saveFile
from myMusicDBMap import myMusicDBMap
from musicDBData import musicDBData
from musicArtistData import musicArtistData
        
class musicData:
    def __init__(self, init=False):
        ext = "p"
        self.mapfilename  = "musicData.{0}".format(ext)
        self.mapname      = join(prefix, 'musicdb', self.mapfilename)
        self.masterdfname = join(prefix, 'musicdb', "masterMusicData.{0}".format(ext))
        if init is True:
            self.artists = {}
        else:
            try:
                self.artists     = getFile(ifile=self.mapname, debug=True)
            except:
                print("Could not find previous data {0}".format(self.mapname))
                self.artists = {}

        
    ################################################################################################
    ## DB Data
    ################################################################################################
    def setDBData(self, source, dbdata, debug=False):
        if isinstance(dbdata, dict):
            if debug:
                print("====> Will add {0} entries for source {1}".format(len(dbdata), source))
            for artistName, artistData in dbdata.items():
                if self.artists.get(artistName) is not None:
                    mad = self.artists[artistName]
                else:
                    mad = musicArtistData(discname=artistName)
                mad.addDBData(source=source, dbdata=artistData)
                self.artists[artistName] = mad
            if debug:
                print("\tAfter adding {0} entries for source {1} there are now {2} artist entries".format(len(dbdata), source, len(self.artists)))
        else:
            raise ValueError("Must pass music dict")
            
        
    ################################################################################################
    ## Music DB Data
    ################################################################################################
    def setMusicDBData(self, mdb, debug=False):
        self.setDBData(source="Music", dbdata=mdb.get(), debug=debug)
            
        
    ################################################################################################
    ## Chart DB Data
    ################################################################################################
    def setChartDBData(self, chart, chartdb, debug=False):
        self.setDBData(source=chart, dbdata=chartdb, debug=debug)
        
        
    ################################################################################################
    ## Rename Data
    ################################################################################################
    def setRenameData(self, renameData, debug=False):
        source = "Renames"
        if isinstance(renameData, dict):
            if debug:
                print("====> Will add {0} entries for source {1}".format(len(renameData), source))
            for renameName, artistName in renameData.items():
                if self.artists.get(artistName) is not None:
                    mad = self.artists[artistName]
                else:
                    mad = musicArtistData(discname=artistName)
                mad.addRenames(renameName)
                self.artists[artistName] = mad
            if debug:
                print("\tAfter adding {0} entries for source {1} there are now {2} artist entries".format(len(renameData), source, len(self.artists)))
        else:
            raise ValueError("Must pass music dict")
        
        
    
    ################################################################################################
    ## General Utils
    ################################################################################################
    def getArtistData(self, artistName):
        if self.artists.get(artistName):
            return self.artists[artistName]
        else:
            print("Could not find artist {0} in music DB.".format(artistName))
        return None
        
    def save(self, artists=None):
        if artists is None:
            artists = self.artists
        self.show(artists)
        saveFile(idata=artists, ifile=self.mapname, debug=True)

    def show(self, artists=None):
        if artists is None:
            artists = self.artists
        print("There are {0} known artists".format(len(artists)))
        
            
            
    ################################################################################################
    ## Master DataFrame
    ################################################################################################
    def getMasterDBStatus(self, alldf):
        alldf["Status"] = alldf.apply(func=lambda x: x.nunique(), axis=1)
        return alldf
        
    def createMasterDF(self, artists=None):
        if artists is None:
            artists = self.artists
        if artists is None:
            artists = getFile(ifile=self.mapname, debug=True)
        
        tmp = {artistName: artists[artistName].dfSummary() for artistName in artists.keys()}
        alldf = concat(tmp.values(), keys=tmp.keys())
        alldf = self.getMasterDBStatus(alldf)
        alldf.index.names = ["Artist", "DB"]
        
        saveFile(idata=alldf, ifile=self.masterdfname, debug=True)
            
        
    
    ################################################################################################
    ## Summary
    ################################################################################################
    def summary(self):
        for artist in self.artists.keys():
            artistData = self.artists[artist]
            artistData.summary()
            print("="*100,"\n")