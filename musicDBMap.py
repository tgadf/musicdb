from collections import Counter
from ioUtils import getFile, saveFile
from searchUtils import findNearest
from os import getcwd
from os.path import join
from sys import prefix
from artistDB import artistDB
from pandas import Series, DataFrame

from musicDBArtistMap import myMusicArtistDBData, musicDBKey

class musicDBMap:
    def __init__(self, source, debug=False, init=False, copy=False):
        self.source=source
        self.debug=debug
        if debug:
            print("Creating myMusicDBMap()")            

        #### Database locations
        self.setMapname(source)
        self.mdbKey = musicDBKey(source)
        
        
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
        return list(self.musicmap.values())
    
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
    def getPrimaryKey(self, artistName=None, artistID=None):
        primaryKey = self.mdbKey.getKey(artistName=artistName, artistID=artistID)
        return primaryKey
        
    def isKnownByKey(self, primaryKey):
        if self.musicmap.get(primaryKey) is None:
            return False
        return True
    
    def isKnownByName(self, artistName):
        primaryKey = self.getPrimaryKey(artistName=artistName, artistID=None)
        return self.isKnownByKey(primaryKey)
    
    def isKnownByID(self, artistID):
        primaryKey = self.getPrimaryKey(artistName=None, artistID=artistID)
        return self.isKnownByKey(primaryKey)
    
    
    ###################################################################################################
    # Add/Remove Artists
    ###################################################################################################
    def addArtistByKey(self, primaryKey, artistName=None, artistID=None):
        if not self.isKnownByKey(primaryKey):
            print("Adding PrimaryKey: {0}".format(primaryKey))
            self.musicmap[primaryKey] = myMusicArtistDBData(primaryKey=primaryKey, artistName=artistName, artistID=artistID)
            
    def removeArtistByKey(self, primaryKey):
        if self.isKnownByKey(primaryKey):
            print("Removing PrimaryKey: {0}".format(primaryKey))
            del self.musicmap[primaryKey]
        else:
            print("Could not remove PrimaryKey: {0}".format(primaryKey))
            
    def addArtistByName(self, artistName):
        primaryKey = self.getPrimaryKey(artistName=artistName)
        if not self.isKnownByKey(primaryKey):
            print("Adding PrimaryKey (From Name [{0}]): {1}".format(artistName, primaryKey))
            self.musicmap[primaryKey] = myMusicArtistDBData(primaryKey=primaryKey, artistName=artistName, artistID=None)
        
    def removeArtistByName(self, artistName):
        primaryKey = self.getPrimaryKey(artistName=artistName)
        if self.isKnownByKey(primaryKey):
            print("Removing PrimaryKey (From Name [{0}]): {1}".format(artistName, primaryKey))
            del self.musicmap[primaryKey]
        else:
            print("Could not remove PrimaryKey From Name: {0}".format(artistName))
        
    def addArtistByID(self, artistName):
        primaryKey = self.getPrimaryKey(artistID=artistID)
        if not self.isKnownByKey(primaryKey):
            print("Adding PrimaryKey (From ID [{0}]): {1}".format(artistID, primaryKey))
            self.musicmap[primaryKey] = myMusicArtistDBData(primaryKey=primaryKey, artistName=None, artistID=artistID)
        
    def removeArtistByID(self, artistID):
        primaryKey = self.getPrimaryKey(artistID=artistID)
        if self.isKnownByKey(primaryKey):
            print("Removing PrimaryKey (From ID [{0}]): {1}".format(artistID, primaryKey))
            del self.musicmap[primaryKey]
        else:
            print("Could not remove PrimaryKey From ID: {0}".format(artistID))
        
    
    ###################################################################################################
    # Add/Remove Artist Data
    ###################################################################################################
    def getArtistDataByKey(self, primaryKey):
        if self.isKnownByKey(primaryKey):
            return self.musicmap[primaryKey]
        else:
            print("Could not find artist data from PrimaryKey: {0}".format(primaryKey))
        return None
            
    def addArtistDataByKey(self, primaryKey, db, dbID):
        if self.isKnownByKey(primaryKey):
            self.musicmap[primaryKey].add(db, dbID)
            print("Added DB/ID [{0}/{1}] to Primary Key: {2}".format(db, dbID, primaryKey))
        else:
            print("Could not add artist data from PrimaryKey: {0}".format(primaryKey))
            
            
    def getArtistDataByName(self, artistName):
        primaryKey = self.getPrimaryKey(artistName=artistName, artistID=None)
        if self.isKnownByKey(primaryKey):
            return self.musicmap[primaryKey]
        else:
            print("Could not find artist data from PrimaryKey (From Name [{0}]): {1}".format(artistName, primaryKey))
        return None
            
    def addArtistDataByName(self, artistName, db, dbID):
        primaryKey = self.getPrimaryKey(artistName=artistName, artistID=None)
        if self.isKnownByKey(primaryKey):
            self.musicmap[primaryKey].add(db, dbID)
            print("Added DB/ID [{0}/{1}] to Primary Key: {2}".format(db, dbID, primaryKey))
        else:
            print("Could not add artist data from PrimaryKey (From Name [{0}]): {1}".format(artistName, primaryKey))
            
    def getArtistDataByID(self, artistID):
        primaryKey = self.getPrimaryKeyFrom(artistName=None, artistID=artistID)
        if self.isKnownByKey(primaryKey):
            return self.musicmap[primaryKey]
        else:
            print("Could not find artist data from PrimaryKey (From ID [{0}]): {1}".format(artistID, primaryKey))
        return None
            
    def addArtistDataByID(self, artistID, db, dbID):
        primaryKey = self.getPrimaryKey(artistName=None, artistID=artistID)
        if self.isKnownByKey(primaryKey):
            self.musicmap[primaryKey].add(db, dbID)
            print("Added DB/ID [{0}/{1}] to Primary Key: {2}".format(db, dbID, primaryKey))
        else:
            print("Could not add artist data from PrimaryKey (From ID [{0}]): {1}".format(artistID, primaryKey))
            
        
        
        
        
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