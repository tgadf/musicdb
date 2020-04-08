from discogsBase import discogs
from masterdb import getArtistAlbumsDB
from searchUtils import findNearest
from pandas import DataFrame


########################################################################################################
#
# Set Artist Database
#
########################################################################################################
class artistDB():
    def __init__(self, db, debug=False):
        self.db    = db
        self.debug = debug
        if debug:
            print("Getting DB Data For {0}".format(db))
        
        try:
            self.disc           = discogs(db.lower())
        except:
            raise ValueError("Cannot create a discogs() object with [{0}]".format(db.lower()))
            
        self.discdf         = None
        self.artists        = None
        self.artistIDToName = None
        self.artistNameToID = None
        self.artistAlbumsDB = None
        self.Nalbums        = None
        
        self.setArtistIDMap()
        self.setAlbumIDMap()
        self.summary()
            
            
    ########################################################################################################
    #
    # Set Artist ID Mapping
    #
    ########################################################################################################
    def setArtistIDMap(self):        
        if self.debug:
            print("  Getting Master Artist DB File ({0})".format(self.db))

        self.discdf  = self.disc.getMasterSlimArtistDiscogsDB()
        self.artists = [x for x in list(self.discdf["DiscArtist"]) if x is not None]
        if self.debug:
            print("    Found {0} Artists in DB".format(len(self.artists)))

        self.artistIDToName = self.discdf["DiscArtist"].to_dict()
        self.artistNameToID = {}
        if self.debug:
            print("    Found {0} ID -> Name entries".format(len(self.artistIDToName)))

        for artistID,artistName in self.artistIDToName.items():
            if artistName is None:
                continue
            if self.artistNameToID.get(artistName) is None:
                self.artistNameToID[artistName] = []
            self.artistNameToID[artistName].append(artistID)
        if self.debug:
            print("    Found {0} Name -> ID entries".format(len(self.artistNameToID)))
            
            
    ########################################################################################################
    #
    # Set Artist Album ID Mapping
    #
    ########################################################################################################
    def setAlbumIDMap(self):        
        if self.debug:
            print("  Getting Master Artist Album DB File ({0})".format(self.db))
            
        self.albumsDB = getArtistAlbumsDB(self.disc, force=False).to_dict()
        if self.debug:
            print("    Found {0} Artist Albums".format(len(self.albumsDB)))
            
        try:
            self.albumsDB = self.albumsDB["Albums"]
        except:
            raise ValueErrors("Error getting Albums from Artist Albums Database")
        
            
            
    ########################################################################################################
    #
    # Get Artist Data
    #
    ########################################################################################################
    def getArtistIDs(self, artistName, num=10, cutoff=0.7, debug=False):
        artistIDs = {}
        if self.artistNameToID.get(artistName) is not None:
            artistIDs[artistName] = self.artistNameToID[artistName]
            return artistIDs
        elif num is None or cutoff is None:
            return {}
        else:
            nearArtists = findNearest(artistName, self.getArtists(), num=num, cutoff=cutoff)
            if debug:
                print("Nearest Matches for: {0}".format(artistName))
            for nearArtist in nearArtists:
                artistIDs[nearArtist] = self.artistNameToID[nearArtist]
            return artistIDs
        
        return artistIDs
    
    
    def getArtistAlbums(self, artistID):
        if self.albumsDB.get(artistID) is None:
            print("Artist ID [{0}] is not found in Albums DB [{1}]".format(artistID, self.db))
            return {}
        return self.albumsDB[artistID]

            
            
    ########################################################################################################
    #
    # Summarize Artist Data
    #
    ########################################################################################################
    def getArtists(self):
        return self.artists
    
    def getNartistIDs(self):
        return len(self.artistIDToName)

    def getNartistNames(self):
        return len(self.artistNameToID)
    
    def getNalbums(self):
        try:
            nAlbums = sum([[len(v2) for v2 in v.values()][0] for k,v in self.albumsDB.items()])
        except:
            nAlbums = 0
        return nAlbums
    
    
    
    def summary(self):
        print("Summary Statistics For DB: {0}".format(self.db))
        print("    Found {0} ID -> Name entries".format(self.getNartistIDs()))
        print("    Found {0} Name -> ID entries".format(self.getNartistNames()))
        print("    Found {0} Albums".format(self.getNalbums()))