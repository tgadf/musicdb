from collections import Counter
from ioUtils import getFile, saveFile
from searchUtils import findNearest
from os import getcwd
from os.path import join
from sys import prefix
from artistDB import artistDB
from pandas import Series, DataFrame
from hashlib import md5


class myMusicDBs:
    def __init__(self):
        self.dbs = ["Discogs", "AllMusic", "MusicBrainz", "AceBootlegs", "RateYourMusic", "LastFM", "DatPiff", "RockCorner", "CDandLP", "MusicStack", "MetalStorm"]
    
    def isValid(self, db):
        return db in self.dbs
    
    def getDBs(self):
        return self.dbs
        
        
        

class myMusicDBIDData:
    def __init__(self, dbID=None):
        self.dbID = None
        self.name = None
        
    def add(self, dbID, name=None):
        if dbID is None:
            self.dbID = dbID
            self.name = name
            return
        
        try:
            str(int(dbID))
        except:
            raise ValueError("Cannot set dbID to {0}".format(dbID))
            
        self.dbID = str(dbID)
        self.name = name
        
    def get(self):
        return (self.dbID,self.name)
            
        
        

class myMusicArtistDBData(myMusicDBs):
    def __init__(self):
        myMusicDBs.__init__(self)
        self.init()
        
    def init(self):
        self.dbdata = {db: myMusicDBIDData() for db in self.getDBs()}
        
    def add(self, db, dbID=None):
        assert self.isValid(db)
        self.dbdata[db].add(dbID, name=None)
        
    def show(self):
        print("{0: <20}{1}".format("DB", "Value"))
        for db,dbIDdata in self.dbdata.items():
            print("{0: <20}{1}".format(db,dbIDdata.get()))
            
    def getSeries(self):
        sdata = Series({db: dbIDdata.dbID for db,dbIDdata in self.dbdata.items()})
        return sdata
    
    def getDBData(self, db):
        if self.dbdata.get(db) is not None:
            return self.dbdata[db]
        return None
            
    def getDBID(self, db):
        if self.dbdata.get(db) is not None:
            return self.dbdata[db].dbID
        return None    
    
    def getDict(self):
        dfdata = {db: dbIDdata.dbID for db,dbIDdata in self.dbdata.items()}
        return dfdata
        
    def getDF(self):
        dfdata = DataFrame(Series({db: dbIDdata.dbID for db,dbIDdata in self.dbdata.items()}))
        return dfdata
        
    def get(self):
        return self.dbdata
    
    


class musicDBMap:
    def __init__(self, source, debug=False, init=False):
        self.source=source
        self.debug=debug
        if debug:
            print("Creating myMusicDBMap()")            

        #### Database locations
        self.setMapname(source)
        
        #### Load Previous Matches
        if init is True:
            self.clean()
        else:
            self.load()
            
        self.info()
        
        
        
    ###################################################################################################
    # General
    ###################################################################################################
    def setMapname(self, source):
        self.mapfilename = 'db{0}Map.p'.format(source)
        self.mapname     = join(prefix, 'musicdb', self.mapfilename)
        
    def clean(self):
        self.musicmap = {}
        
    def stats(self):
        stats = {}        
        for primaryKey,dbData in self.musicmap.items():
            for db,dbID in dbData.getDict().items():
                if stats.get(db) is None:
                    stats[db] = 0
                if dbID is not None:
                    stats[db] += 1
        print("{0: <20}{1: <7}{2}".format("", "Counts", "Fraction"))        
        for db,stat in stats.items():
            print("{0: <20}{1: <7}{2: >2}".format(db, stat, int(round(100*stat/len(self.musicmap), 0))))
        
    def update(self, dbdump):
        if not isinstance(dbdump, dict):
            raise ValueError("Update will only work on a dict dump of the DB")
        self.clean()
        for primaryKey,dbData in dbdump.items():
            artistName = primaryKey[0]
            artistID   = primaryKey[1]
            self.addArtist(artistName, artistID)
            for db,dbID in dbData.items():
                self.addArtistData(artistName, artistID, db, dbID)
        print("There are now {0} updated matched entries.".format(len(self.musicmap)))
        
    def dump(self):
        dump = {}
        for primaryKey,dbData in self.musicmap.items():
            dump[primaryKey] = {db: dbval.dbID for db,dbval in dbData.get().items()}
        saveFile(idata=dump, ifile="dbDump.p")
        
    def getSize(self):
        return len(self.musicmap)
        
    def info(self):
        print("  Loaded {0} previously matched entries".format(self.getSize()))
        #for primaryKey,dbdata in self.musicmap.items():
        #    for db,dbvalue in dbdata
        #cntr = Counter()
        
        
    ###################################################################################################
    # Lists / DF / Series
    ###################################################################################################
    def getArtists(self):
        return list(self.musicmap.keys())
    
    def getDF(self):
        dfdata = DataFrame({primaryKey: artistData.getSeries() for primaryKey,artistData in self.musicmap.items()})
        return dfdata
    
    def getDB(self, db):
        try:
            dfdata = self.getDF().T
            dbdata = DataFrame(df[db])
        except:
            raise ValueError("Could not get DB matched data for {0}".format(db))
        return dbdata
        
        
        
    ###################################################################################################
    # Primary Key (Artist <-> Hash)
    ###################################################################################################
    def getHash(self, name):
        m = md5()
        m.update(name.encode('utf-8'))
        retval = m.hexdigest()
        return retval
    
    def getPrimaryKey(self, artistName, artistID):
        return (artistName, artistID)
    
    def getPrimaryKeyFromID(self, artistID):
        primaryKeys = []
        for primaryKey in self.getArtists():
            if primaryKey[1] == artistID:
                primaryKeys.append(primaryKey)
        if len(primaryKeys) != 1:
            print("Could not get PrimaryKey from AritsID [{0}]".format(artistID))
            return None
        return primaryKeys[0]
    
    def isKnownKey(self, primaryKey):
        if self.musicmap.get(primaryKey) is None:
            return False
        return True
        
    def isKnown(self, artistName, artistID):
        primaryKey = self.getPrimaryKey(artistName, artistID)
        return self.isKnownKey(primaryKey)
    
    def addArtist(self, artistName, artistID=None):
        if artistID is None:
            artistID = self.getHash(artistName)
        primaryKey = self.getPrimaryKey(artistName, artistID)
        if not self.isKnown(artistName, artistID):
            self.musicmap[primaryKey] = myMusicArtistDBData()
        else:
            if self.debug:
                print("Will not add artist ({0}) because it is already known".format(primaryKey))
            
    def removeArtist(self, artistName, artistID=None):
        if artistID is None:
            artistID = self.getHash(artistName)
        primaryKey = self.getPrimaryKey(artistName, artistID)
        if not self.isKnown(artistName, artistID):
            if self.debug:
                print("Will not remove artist ({0}) because it is not known".format(primaryKey))
        del self.musicmap[primaryKey]
        
        
        
    ###################################################################################################
    # Secondary Key (Artist DB Data)
    ###################################################################################################
    def getArtistData(self, artistName, artistID=None):
        if artistID is None:
            artistID = self.getHash(artistName)
        primaryKey = self.getPrimaryKey(artistName, artistID)
        if not self.isKnown(artistName, artistID):
            if self.debug:
                print("Can not get artist data ({0}) because it is not known".format(primaryKey))
        return self.musicmap[primaryKey]
           
    def getArtistDataByID(self, artistID):
        primaryKey = self.getPrimaryKeyFromID(artistID)        
        if not self.isKnownKey(primaryKey):
            if self.debug:
                print("Can not get artist data ({0}) because it is not known".format(primaryKey))
        return self.musicmap[primaryKey]
           
    def add(self, artistName, artistID, db, dbID):
        self.addArtistData(artistName, artistID, db, dbID)
        
    def addArtistData(self, artistName, artistID, db, dbID):
        if artistID is None:
            artistID = self.getHash(artistName)
        primaryKey = self.getPrimaryKey(artistName, artistID)
        if not self.isKnown(artistName, artistID):
            if self.debug:
                print("Can not add artist data ({0}) because it is not known".format(primaryKey))
        self.musicmap[primaryKey].add(db, dbID)
        
        
        
        
    ###################################################################################################
    # I/O
    ###################################################################################################
    def get(self):
        if self.debug:
            print("Found {0} artist entries".format(len(self.musicmap)))
        return self.musicmap
    
    def load(self):        
        if self.debug:
            print("   Loading my music db map: {0}".format(self.mapname))
        try:
            self.musicmap = getFile(ifile=self.mapname)
        except:
            raise ValueError("Could not open {0}".format(self.mapname))        
    
    def save(self, musicmap=None):
        if musicmap is None:
            musicmap = self.musicmap
        saveFile(idata=musicmap, ifile=self.mapname, debug=True)
        
    def saveYAML(self):
        savename      = self.mapfilename.replace(".p", ".yaml")
        musicmap = self.get()
        saveFile(idata=musicmap, ifile=savename, debug=True)
        
    def readYAML(self):
        savename      = self.mapfilename.replace(".p", ".yaml")
        musicmap = getFile(savename)
        self.save(musicmap)