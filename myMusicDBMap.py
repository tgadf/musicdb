from collections import Counter
from ioUtils import getFile, saveFile
from searchUtils import findNearest
from os import getcwd
from os.path import join
from sys import prefix
from artistDB import artistDB
import json

class myMusicDBMap():
    def __init__(self, debug=False, overwrite=False):
        self.debug=debug
        if debug:
            print("Creating myMusicDBMap()")
            

        self.mapfilename = 'myMusicMap.p'
        self.mapname     = join(prefix, 'musicdb', self.mapfilename)
        
        
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
            
    
        if overwrite is False:
            self.setAlbumTypes()
            self.setDBMatches()

            if debug:
                self.show()
        else:
            print("Go ahead and edit the music map")
            
            
    def checkDB(self, db, artist=None):
        if db not in self.dbkeys:
            if artist is None:
                artist = "?"
            raise ValueError("Database [{0}] not in valid DB list (Artist is {1})".format(db, artist))            
            
    def setDBs(self, dbs):
        self.dbkeys = dbs
                        
    def checkID(self, dbID, db=None, artist=None):
        if dbID is None:
            return
        try:
            int(dbID)
        except:
            if db is None:
                db = "?"
            if artist is None:
                artist = "?"
            raise ValueError("Database ID [{0}] is not an integer (DB is {1} and Artist is {2})".format(dbID, db, artist))            
            
            
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
        
    def saveYAML(self):
        savename      = self.mapfilename.replace(".p", ".yaml")
        musicmap = self.get()
        saveFile(idata=musicmap, ifile=savename, debug=True)
        
    def readYAML(self):
        savename      = self.mapfilename.replace(".p", ".yaml")
        musicmap = getFile(savename)
        self.save(musicmap)
            

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
        

    def initKey(self, db):
        for myArtistName in self.musicmap.keys():
            self.musicmap[myArtistName][db] = None
        return self.musicmap
        #self.saveMyMusicMap()
        

    def rmArtist(self, artistName):
        if self.musicmap.get(artistName) is None:
            print("There is no artist [{0}] in music DB.".format(artistName))
            return
        del self.musicmap[artistName]
        return
        print("Could not delete db [{0}] for artist [{1}] in music DB.".format(db, artistName))
        

    def rmArtistDBKey(self, artistName, db):
        if self.musicmap.get(artistName) is None:
            print("There is no artist [{0}] in music DB.".format(artistName))
            return
        
        if self.musicmap[artistName].get(db) is not None:
            del self.musicmap[artistName][db]
        return
        print("Could not delete db [{0}] for artist [{1}] in music DB.".format(db, artistName))


        
    def rmKey(self, db):
        self.checkDB(db)
        for myArtistName in self.musicmap.keys():
            self.rmArtistDBKey(artistName, db)
        return self.musicmap
        #self.saveMyMusicMap()
        
        
    def addArtist(self, artistName):
        if self.musicmap.get(artistName) is None:
            print("Adding Artist {0}".format(artistName))
            self.musicmap[artistName] = {db: None for db in self.getDBs()}
            print("\t",self.musicmap[artistName])
        
        
    def add(self, artistName, dbName, artistID):
        self.checkDB(dbName)
        self.checkID(artistID)
        
        try:
            int(artistID)
        except:
            raise ValueError("Artist [{0}}] and Database [{1}] with ID [{2}] isn't a number".format(dbName, artistName, artistID))
        
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
    # DB Section
    #
    ####################################################################################################
    def getDBMatches(self, db):
        dbMatches = {}
        for artistName in self.getArtists():
            dbData = self.getArtistDBData(artistName, db)
            if dbData.get('ID') is not None:
                dbMatches[artistName] = dbData['ID']
        return dbMatches
    
    
    def setDBMatches(self):
        self.dbArtistData = {db: {} for db in self.getDBs()}
        for artist,artistData in self.get().items():
            for db,dbmatch in artistData.items():
                self.checkDB(db,artist)
                if dbmatch is not None:
                    dbID = dbmatch.get('ID')
                    self.checkID(dbID)
                    self.dbArtistData[db][dbID] = artist
                    
    
        
    ####################################################################################################
    #
    # Artist Section
    #
    ####################################################################################################
    def isKnown(self, artistName):
        if self.musicmap.get(artistName) is None:
            return False
        return True
        
    def getArtistFromID(self, dbID):
        for artistName,artistData in self.musicmap.items():
            for db,dbdata in artistData.items():
                if dbdata is not None:
                    dbdataID = dbdata.get("ID")
                    if dbdataID == dbID:
                        return [db,artistName]
        return [None,None]
        
        
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
    
    
    def getArtistDataIDs(self, artistName, returnNone=True):
        if self.musicmap.get(artistName) is None:
            return {}        
        
        retval = {}
        for db,dbdata in self.musicmap[artistName].items():
            try:
                ID = dbdata["ID"]
            except:
                ID = None
                if returnNone is False:
                    continue
            retval[db] = ID
        return retval
    
    
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
    def getArtistIDsFromDBs(self, artistName, dbs, num=10, cutoff=0.7, debug=False):
        if not all([self.dbdata.get(db) for db in self.getDBs()]):
            self.getFullDBData()
                    
        if debug:
            print("  Getting DB Artist IDs for ArtistName: {0}".format(artistName))
        artistIDs = {}
        for db in self.getDBs():
            if db in dbs:
                artistIDs[db] = self.getArtistDBIDs(artistName, db, num, cutoff, debug)
            else:
                artistIDs[db] = {}
        return artistIDs
    
    
    
    def getArtistIDs(self, artistName, num=10, cutoff=0.7, debug=False):
        if not all([self.dbdata.get(db) for db in self.getDBs()]):
            self.getFullDBData()
                    
        if debug:
            print("  Getting DB Artist IDs for ArtistName: {0}".format(artistName))
        artistIDs = {db: self.dbdata[db].getArtistIDs(artistName, num, cutoff, debug=debug) for db in self.getDBs()}
        return artistIDs
    
    
    def getArtistFromDBID(self, db, dbID):
        try:
            adb = self.dbdata[db]
        except:
            raise ValueError("DB {0} does not exist.".format(db))
            
        artist = adb.getArtistNameFromID(dbID)
        return artist
        
        
    def getArtistDBIDs(self, artistName, db, num=10, cutoff=0.7, debug=False):
        if self.dbdata.get(db) is None:
            self.getFullDBData()
                    
        if debug:
            print("  Getting DB Artist IDs for ArtistName: {0}".format(artistName))
        artistIDs = self.dbdata[db].getArtistIDs(artistName, num, cutoff, debug=debug)
        return artistIDs
        
        
            
    ########################################################################################################
    #
    # Get Artist Album Data
    #
    ########################################################################################################
    def getArtistAlbumsFromID(self, db, artistID, flatten=False):
        if not all([self.dbdata.get(db) for db in self.getDBs()]):
            self.getFullDBData()
        artistAlbums = self.dbdata[db].getArtistAlbums(artistID, flatten=flatten)
        return artistAlbums
    
    
    def getArtistAlbums(self, artistName, num=10, cutoff=0.7, debug=False):
        if not all([self.dbdata.get(db) for db in self.getDBs()]):
            self.getFullDBData()
        
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
    def getNearestArtistNames(self, artistName, num=1, cutoff=0.9, debug=False):
        if not all([self.dbdata.get(db) for db in self.getDBs()]):
            self.getFullDBData()
        artistMatches = {db: self.dbdata[db].getNearestArtist(artistName, num, cutoff, debug=debug) for db in self.getDBs()}
        return artistMatches
        
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
    def getSubsetData(self, dbname):
        mydbdata = {artistName: db.get(dbname) for artistName, db in self.musicmap.items() if db.get(dbname) is not None}
        mydbdata = {artistName: dbdata.get("ID") for artistName, dbdata in mydbdata.items() if dbdata.get("ID") is not None}
        return mydbdata

        
    def getDBData(self, db, known=False):
        if db not in self.getDBs():
            raise ValueError("Nothing known about DB [{0}]".format(db))
            
        if self.debug:
            print("Getting Database Data For {0}".format(db))
            
        if known is True:
            if self.debug is True:
                print("Loading Subset of Database Data For {0}".format(db))
            
        dbdata = artistDB(db, known=known, debug=self.debug)
        return dbdata
    
    
    def getFullDBData(self):
        for db in self.getDBs():
            self.dbdata[db] = self.getDBData(db, known=False)
    
        
    def getKnownDBData(self):
        for db in self.getDBs():
            self.dbdata[db] = self.getDBData(db, known=True)
        
        
        
    ####################################################################################################
    #
    # Database Section
    #
    ####################################################################################################
    def getDBAlbumTypeNames(self, db, albumType):
        albumTypes = self.getDBAlbumTypes(db)
        try:
            albumTypeNames = albumTypes[albumType]
        except:
            raise ValueError("Could not find DB AlbumType [{0}] for DB [{1}] in dbAlbumTypes".format(albumType, db))
            
        return albumTypeNames
        
        
    def getDBAlbumTypes(self, db):
        try:
            dbAlbumTypes = self.dbAlbumTypes[db]
        except:
            raise ValueError("Could not find DB [{0}] in dbAlbumTypes".format(db))
            
        return dbAlbumTypes
    
            
    def setAlbumTypes(self):
        self.dbAlbumTypes = {}
                     
        for db in self.getDBs():
            if db == "Discogs":
                allTypes  = ["Albums", "Singles & EPs", "Compilations", "Videos", "Miscellaneous"]
                primary   = ["Albums"]
                secondary = ["Compilations"]
                tertiary  = ["Singles & EPs"]
                fourth    = ["Videos", "Miscellaneous"] 
            elif db == "AllMusic":
                allTypes  = ["Albums", "Single/EP", "Comp", "Video", "Other"]
                primary   = ["Albums"]
                secondary = ["Comp"]
                tertiary  = ["Single/EP"]
                fourth    = ["Video", "Other"]
            elif db == "MusicBrainz":
                primary   = ["Album", "Album + Live", "Album + Soundtrack", "Album + Mixtape/Street", "Album + Remix", "Album + Audiobook", "Album + DJ-mix", "Album + Demo", "Album + Spokenword", "Album + Audio drama", "Album + Spokenword + Live", "Album + Soundtrack + Live", "Album + Remix + Mixtape/Street", "Album + Spokenword + Audiobook", "Album + Interview", "Album + Live + DJ-mix", "Album + Soundtrack + Remix", "Album + DJ-mix + Mixtape/Street", "Album + Interview + Live", "Album + Remix + DJ-mix", "Album + Live + Remix", "Album + Soundtrack + Audiobook", "Album + Interview + Demo", "Album + Soundtrack + Spokenword + Interview", "Album + Live + Demo", "Album + Soundtrack + Spokenword", "Album + Spokenword + Interview", "Album + Remix + Mixtape/Street + Demo", "Album + Demo + Audio drama", "Album + Soundtrack + Audiobook + Audio drama", "Album + Spokenword + Interview + Audiobook", "Album + Spokenword + Demo", "Album + Interview + Audiobook + Audio drama", "Album + Soundtrack + Audio drama", "Album + Soundtrack + Interview + Live", "Album + Audiobook + Audio drama", "Album + Audiobook + Live", "Album + Soundtrack + Demo"]
                secondary = ["Album + Compilation", "Album + Compilation + DJ-mix", "Compilation", "Album + Compilation + Live", "Album + Compilation + Soundtrack", "Album + Compilation + Remix", "Single + Compilation", "Album + Compilation + Mixtape/Street", "Album + Compilation + Live + DJ-mix", "Album + Compilation + Spokenword", "Album + Compilation + Demo", "Broadcast + Compilation", "Compilation + DJ-mix", "Album + Compilation + DJ-mix + Mixtape/Street", "Album + Compilation + Remix + DJ-mix", "Album + Compilation + Spokenword + Live", "Album + Compilation + Soundtrack + Remix", "Album + Compilation + Interview", "Compilation + Soundtrack", "Compilation + Live", "Broadcast + Compilation + Live", "Album + Compilation + Interview + Live", "Album + Compilation + Audio drama", "Album + Compilation + Audiobook", "Album + Compilation + Live + Demo", "Album + Compilation + Live + Remix", "Compilation + Live + DJ-mix", "Album + Compilation + Spokenword + Audiobook", "Broadcast + Compilation + Remix + DJ-mix", "Album + Compilation + Mixtape/Street + Demo", "Album + Compilation + Soundtrack + Interview", "Album + Compilation + Soundtrack + Spokenword + Interview + Audiobook + Remix", "Album + Compilation + Remix + Mixtape/Street", "Compilation + Remix", "Album + Compilation + Soundtrack + Demo", "Broadcast + Compilation + Audio drama"]
                tertiary  = ["Single", "EP", "EP + Live", "EP + Remix", "Single + Soundtrack", "Single + Live", "EP + Demo", "EP + Compilation", "EP + Soundtrack", "EP + Mixtape/Street", "Single + Demo", "Single + DJ-mix", "Single + Mixtape/Street", "EP + DJ-mix", "Single + Soundtrack + Remix", "Single + Audiobook", "EP + Compilation + Remix", "Single + Live + Remix", "EP + Live + Demo", "EP + Audio drama", "EP + Remix + Mixtape/Street", "Single + Audio drama", "Single + Soundtrack + Live", "EP + Soundtrack + Remix", "EP + Compilation + Live", "EP + Compilation + Mixtape/Street", "EP + Audiobook", "Single + Compilation + Remix", "Single + DJ-mix + Demo", "EP + Compilation + Remix + DJ-mix", "EP + Live + DJ-mix", "EP + Spokenword + Live", "Single + Remix + Mixtape/Street", "Single + Remix + Demo", "EP + Compilation + Demo", "Single + Mixtape/Street + Demo", "EP + Live + Remix", "Single + Spokenword", "Single + Interview", "EP + Compilation + Soundtrack", "EP + Interview"]
                fourth    = ["Unspecified type", "Other", "Single + Remix", "Other + Audiobook", "Other + Audio drama", "Other + Spokenword", "Live", "Remix", "Other + Compilation", "Broadcast", "Audiobook", "Other + Live", "Other + Demo", "Other + Interview", "Broadcast + Live", "Major series / box sets", "Sub Optimal Credits", "Soundtrack", "Broadcast + Audio drama", "Other + Mixtape/Street", "Currently known involved people:", "Demo", "The What The Fuck Serie:", "Mixtape/Street", "Other + DJ-mix", "A stab at the horrible Blue Note mess:", "Other + Soundtrack", "DJ-mix", "Broadcast + DJ-mix", "Spokenword", "Broadcast + Spokenword", "Broadcast + Audiobook", "Nonline discography:", "Other + Remix", "Other + Compilation + Live", "Other + Compilation + Audiobook", "Online discography:", "Former Official Homepage", "Current Members", "Don\'t add these albums here:", "Broadcast + Live + DJ-mix", "Other + Spokenword + Live", "Other + Spokenword + Audiobook", "Other + Spokenword + Audiobook + Audio drama", "Past Members", "Broadcast + Spokenword + Audio drama", "Audio drama", "Broadcast + Interview", "Other + Compilation + Spokenword", "Live + Demo", "Broadcast + Live + Audio drama", "Broadcast + Spokenword + Audiobook", "Other + Compilation + Demo", "Other + Compilation + Interview", "Broadcast + Demo", "Live + DJ-mix", "Other + Compilation + Live + DJ-mix", "DJ-mix + Mixtape/Street", "Other + Soundtrack + Mixtape/Street + Demo", "Zyklen/Reihen:", "Other + Compilation + DJ-mix", "Other + Audiobook + Audio drama", "Other + Compilation + Mixtape/Street", "Other + Remix + Mixtape/Street", "Other + Compilation + Interview + Live", "Broadcast + Soundtrack", "Other + Live + Demo", "Interview", "Jam Today (2)  1979 ~ 1980", "Other + Spokenword + DJ-mix + Mixtape/Street", "Other + Compilation + Remix", "Broadcast + Interview + Live"]        
                allTypes  = primary + secondary + tertiary + fourth
            elif db == "AceBootlegs":
                allTypes  = ["Bootleg"]
                primary   = ["Bootleg"]
                secondary = []
                tertiary  = []
                fourth    = []
            elif db == "RateYourMusic":     
                primary   = ["Album", "Live Album"]
                secondary = ['V/A Compilation', 'Compilation']
                tertiary  = ['Single', 'EP']
                fourth    = ['Bootleg / Unauthorized', 'Appears On', "Video"]        
                allTypes  = primary + secondary + tertiary + fourth
            elif db == "LastFM":
                allTypes  = ["Albums"]
                primary   = ["Albums"]
                secondary = []
                tertiary  = []
                fourth    = []
            elif db == "DatPiff":
                allTypes  = ["MixTape"]
                primary   = ["MixTape"]
                secondary = []
                tertiary  = []
                fourth    = []
            elif db == "RockCorner":
                primary   = ["Albums"]
                secondary = []
                tertiary  = ["Songs"]
                fourth    = []     
                allTypes  = primary + secondary + tertiary + fourth
            elif db == "CDandLP":
                primary   = ["Albums"]
                secondary = []
                tertiary  = []
                fourth    = []     
                allTypes  = primary + secondary + tertiary + fourth
            elif db == "MusicStack":
                primary   = ["Albums"]
                secondary = []
                tertiary  = []
                fourth    = []     
                allTypes  = primary + secondary + tertiary + fourth
            elif db == "MetalStorm":
                primary   = ["Albums"]
                secondary = []
                tertiary  = []
                fourth    = []
                allTypes  = primary + secondary + tertiary + fourth
            else:
                raise ValueError("Key is not known!")


            retval = {"All": allTypes, 1: primary, 2: secondary, 3: tertiary, 4: fourth}

            self.dbAlbumTypes[db] = retval