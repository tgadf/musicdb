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
            
        if str(dbID) == self.dbID:
            return
        self.dbID = str(dbID)
        self.name = name
        
    def get(self):
        return (self.dbID,self.name)
            
        
        

class myMusicArtistDBData(myMusicDBs):
    def __init__(self, primaryKey=None, artistName=None, artistID=None):
        self.primaryKey = primaryKey
        self.artistName = artistName
        self.artistID   = artistID
        myMusicDBs.__init__(self)
        self.init()
        
    def init(self):
        self.dbdata = {db: myMusicDBIDData() for db in self.getDBs()}
        
    def getPrimaryKey(self):
        return self.primaryKey
        
    def getArtistName(self):
        return self.artistName
        
    def getArtistID(self):
        return self.artistID
        
    def add(self, db, dbID=None):
        assert self.isValid(db)
        self.dbdata[db].add(dbID, name=None)
        
    def show(self):
        try:
            print("ArtistName: {0}".format(self.artistName))
        except:
            print("ArtistName: None")
        try:
            print("ArtistID:   {0}".format(self.artistID))
        except:
            print("ArtistID:   None")
            
        print("{0: <20}{1}".format("DB", "Value"))
        for db,dbIDdata in self.dbdata.items():
            print("{0: <20}{1}".format(db,dbIDdata.get()))
            
    def getSeries(self):
        s1 = Series({db: dbIDdata.dbID for db,dbIDdata in self.dbdata.items()})
        s2 = Series({"DBMatches": s1.shape[0] - sum(s1.isna())})
        sdata = s1.append(s2)
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
    
    
class musicDBSourceType(myMusicDBs):
    def __init__(self, source):
        myMusicDBs.__init__(self)
        
        stype = None
        if source in ["Music", "Local"]:
            stype = "local"
        elif self.isValid(source):
            stype = "db"
        elif source in ["Top40", "Billboard", "BillboardYE"]:
            stype = "chart"
        elif source in ["Top40Uber", "BillboardUber"]:
            stype = "chart"
        elif source in ["Test", "test"]:
            stype = "test"
        else:
            raise ValueError("Could not determine music db source type for db [{0}]".format(source))
            
        self.stype = stype
        
    def isLocal(self):
        return self.stype == "local"
        
    def isDB(self):
        return self.stype == "db"
        
    def isChart(self):
        return self.stype == "chart"
        
    def isTest(self):
        return self.stype == "test"
    
    

class musicDBKey:
    def __init__(self, source):
        self.source  = source
        self.mdbType = musicDBSourceType(source)
        
    def getHash(self, name, extra=[]):
        m = md5()
        m.update(name.encode('utf-8'))
        for value in extra:
            m.update(value.encode('utf-8'))
        retval = m.hexdigest()
        return retval
        
    def getKey(self, artistName=None, artistID=None):
        key = None
        
        if self.mdbType.isLocal() or self.mdbType.isTest():
            if artistName is not None:
                artistID = self.getHash(artistName)
                key = artistID
            elif artistID is not None:
                key = artistID
            else:
                raise ValueError("Can only get local db key with an artist name!")
        elif self.mdbType.isChart():
            if artistName is not None:
                artistID = self.getHash(artistName, extra=[self.source])
                key = artistID
            elif artistID is not None:
                key = artistID
            else:
                raise ValueError("Can only get local db key with an artist name!")
        elif self.mdbType.isDB():
            if artistID is not None:
                key = artistID
            else:
                raise ValueError("Can only get local db key with an artist ID!")
                
        if key is None:
            raise ValueError("Key is NONE!!!")
            
        return key