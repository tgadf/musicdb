from collections import Counter
from ioUtils import getFile, saveFile
from searchUtils import findNearest
from os import getcwd
from os.path import join
from sys import prefix
from artistDB import artistDB

class myMusicDBMap():
    def __init__(self, debug=False):
        self.debug=debug
        if debug:
            print("Creating myMusicDBMap()")
        print(getcwd())
        

        self.mapname  = join(prefix, 'musicdb', 'myMusicMap.p')
        self.dbkeys   = ["Discogs", "AllMusic", "MusicBrainz", "AceBootlegs", "RateYourMusic", "LastFM", "DatPiff", "RockCorner", "CDandLP", "MusicStack", "MetalStorm"]
        #self.dbkeys   = ["AllMusic", "MusicBrainz"]
        #self.dbkeys   = ["AllMusic"]
        self.dbdata   = {}
        
        if debug:
            print("   Loading my music db map: {0}".format(self.mapname))
        try:
            self.musicmap = getFile(ifile=self.mapname)
        except:
            raise ValueError("Could not open {0}".format(self.mapname))
        
        if debug:
            print("   DB keys: {0}".format(self.dbkeys))
            
        if debug:
            self.show()
            
            
    def setDBs(self, dbs):
        self.dbkeys = dbs
            
            
    def get(self):
        if self.debug:
            print("Found {0} artist entries".format(len(self.musicmap)))
        self.show()
        return self.musicmap
    
    
    def getDBs(self):
        return self.dbkeys
    
        
    def save(self, musicmap=None):
        if musicmap is None:
            musicmap = self.musicmap
        self.show(musicmap)
        saveFile(idata=musicmap, ifile=self.mapname, debug=True)
            

    def show(self, musicmap=None):
        if musicmap is None:
            musicmap = self.musicmap
        cntrs = Counter()
        for db in self.getDBs():
            cntrs[db] += 0
        for myArtistName, myArtistData in musicmap.items():
            for dbkey in self.dbkeys:
                if myArtistData.get(dbkey) is not None:
                    cntrs[dbkey] += 1
        print(cntrs)
        
        

    def initKey(self, dbKey):
        for myArtistName in self.musicmap.keys():
            self.musicmap[myArtistName][dbKey] = None
        return self.musicmap
        #self.saveMyMusicMap()
        
        
    def addArtist(self, artistName):
        if self.musicmap.get(artistName) is None:
            print("Adding Artist {0}".format(artistName))
            self.musicmap[artistName] = {db: None for db in self.getDBs()}
            print("\t",self.musicmap[artistName])
        
        
    def add(self, artistName, dbName, artistID):
        if self.musicmap.get(artistName) is None:
            self.addArtist(artistName)
        dbData = self.musicmap[artistName].get(dbName)
        if dbData is None:
            print("Adding Database [{0}] to DB list for [{1}]".format(dbName, artistName))
            self.musicmap[artistName][dbName] = {"ID": None, "Name": None}
        else:
            if self.musicmap[artistName][dbName]["ID"] != artistID:
                print("  Replacing ID for DB [{0}] from [{1}] to [{2}]".format(dbName, self.musicmap[artistName][dbName]["ID"], artistID))
        self.musicmap[artistName][dbName] = {"ID": artistID, "Name": None}
        print("Artist DB Data: {0}".format(self.musicmap[artistName]))
        
        
        
    ####################################################################################################
    #
    # Artist Section
    #
    ####################################################################################################
    def isKnown(self, artistName):
        if self.musicmap.get(artistName) is None:
            return False
        return True
        
        
    def getMatchedDBStatus(self, artistName):
        artistData = self.getArtistData(artistName)
        status     = {}
        for dbkey in self.dbkeys:
            if artistData.get(dbkey) is None:
                status[dbkey] = False
            else:
                status[dbkey] = True
        return status
    
    
    def getArtistData(self, artistName):
        if self.musicmap.get(artistName) is None:
            return {}
        return self.musicmap[artistName]
    
    
    def getArtistDBData(self, artistName, db):
        if self.musicmap.get(artistName) is None:
            return {}
        if self.musicmap[artistName].get(db) is None:
            return {}
        return self.musicmap[artistName][db]
    
    
    def getArtists(self):
        return list(self.musicmap.keys())
    
    
    def showArtistData(self, artistName):
        artistData = self.getArtistData(artistName)
        print("===> {0}".format(artistName))
        for db,dbdata in artistData.items():
            print("   {0: <15}: {1}".format(db,dbdata))
        
            
            
    ########################################################################################################
    #
    # Get Artist Data
    #
    ########################################################################################################
    def getArtistIDs(self, artistName, num=10, cutoff=0.7, debug=False):
        if not all([self.dbdata.get(db) for db in self.getDBs()]):
            self.getFullDBData()
                    
        if debug:
            print("  Getting DB Artist IDs for ArtistName: {0}".format(artistName))
        artistIDs = {db: self.dbdata[db].getArtistIDs(artistName, num, cutoff, debug=debug) for db in self.getDBs()}
        return artistIDs
        
            
            
    ########################################################################################################
    #
    # Get Artist Album Data
    #
    ########################################################################################################
    def getArtistAlbumsFromID(self, db, artistID):
        if not all([self.dbdata.get(db) for db in self.getDBs()]):
            self.getFullDBData()
        artistAlbums = self.dbdata[db].getArtistAlbums(artistID)
        return artistAlbums
    
    
    def getArtistAlbums(self, artistName, num=10, cutoff=0.7, debug=False):
        if not all([self.dbdata.get(db) for db in self.getDBs()]):
            self.getFullDBData()
        
        import json
        print("  Getting Artist Albums for ArtistName: {0}".format(artistName))
        artistAlbums = {}
        artistIDs    = self.getArtistIDs(artistName, num=num, cutoff=cutoff, debug=debug)
        if debug is True:
            print("Found Artist IDs")
            print(artistIDs)
        for db,NameIDs in artistIDs.items():
            artistAlbums[db] = {}
            for name,IDs in NameIDs.items():
                artistAlbums[db][name] = {artistID: self.dbdata[db].getArtistAlbums(artistID) for artistID in IDs}
                
        if debug:
            print("ArtistAlbums({0}) Results".format(artistName))
            for db,nameData in artistAlbums.items():
                print("="*150)
                print("  DB: {0}".format(db))
                for name,IDsData in nameData.items():
                    print("    Name: {0}".format(name))
                    for ID,albums in IDsData.items():
                        print("      ID: {0}".format(ID))
                        for mediaType,mediaData in albums.items():
                            albums = list(mediaData.values())
                            print("          -----> {0: <20} :: {1}\t{2}".format(mediaType, len(albums), json.dumps(albums)))
                        print("\n")
                    print("\n\n")
                        
        return artistAlbums
        
        
        
    ####################################################################################################
    #
    # Interactive Section
    #
    ####################################################################################################
    def getNearestArtists(self, artistName, num=2, cutoff=0.7):
        artists = findNearest(artistName, self.getArtists(), num=num, cutoff=cutoff)
        print("Nearest Matches for: {0}".format(artistName))
        for artist in artists:
            self.showArtistData(artist)
        
        
        
    ####################################################################################################
    #
    # Database Section
    #
    ####################################################################################################
    def getDBData(self, db):
        if db not in self.getDBs():
            raise ValueError("Nothing known about DB [{0}]".format(db))
            
        if self.debug:
            print("Getting Database Data For {0}".format(db))
        dbdata = artistDB(db, debug=self.debug)
        return dbdata
    
        
    def getFullDBData(self):
        for db in self.getDBs():
            self.dbdata[db] = self.getDBData(db)