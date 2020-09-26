from sys import prefix
from os import getcwd
from os.path import join
from ioUtils import getFile, saveFile
from myMusicDBMap import myMusicDBMap
from musicDBData import musicDBData
from musicArtistData import musicArtistData
        
class musicData:
    def __init__(self):
        ext = "p"
        self.mapfilename = "musicData.{0}".format(ext)
        self.mapname     = join(prefix, 'musicdb', self.mapfilename)
        try:
            self.artists     = getFile(ifile=self.mapname, debug=True)
            self.artists = {}
        except:
            print("Could not find previous data {0}".format(self.mapname))
            self.artists = {}

        
    ################################################################################################
    ## DB Data
    ################################################################################################
    def setDBData(self, source, dbdata):
        if isinstance(dbdata, dict):
            for artistName, artistData in dbdata.items():
                if self.artists.get(artistName) is not None:
                    mad = self.artists[artistName]
                else:
                    mad = musicArtistData(discname=artistName)
                mad.addDBData(source=source, dbdata=artistData)
                self.artists[artistName] = mad
        else:
            raise ValueError("Must pass music dict")
            
        
    ################################################################################################
    ## Music DB Data
    ################################################################################################
    def setMusicDBData(self, mdb):
        self.setDBData(source="Music", dbdata=mdb.get())
            
        
    ################################################################################################
    ## Chart DB Data
    ################################################################################################
    def setChartDBData(self, chart, chartdb):
        self.setDBData(source=chart, dbdata=chartdb)
        
        
    ################################################################################################
    ## Rename Data
    ################################################################################################
    def setRenameData(self, renameData):
        if isinstance(renameData, dict):
            for renameName, artistName in renameData.items():
                if self.artists.get(artistName) is not None:
                    mad = self.artists[artistName]
                else:
                    mad = musicArtistData(discname=artistName)
                mad.addRenames(renameName)
                self.artists[artistName] = mad
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
    ## Summary
    ################################################################################################
    def summary(self):
        for artist in self.artists.keys():
            artistData = self.artists[artist]
            artistData.summary()
            print("="*100,"\n")