from pandas import DataFrame
from musicDBData import musicDBData

class musicArtistData:
    def __init__(self, discname):
        self.discname  = discname
        self.usethe    = discname.startswith("The ")

        self.bands     = []
        self.dbdata    = {}

        self.alias     = []
        self.renames   = []

        self.debug = False
        
        
    def dfSummary(self):
        artistDBData = {}
        artistData   = self.dbdata
        artistDBData = {dbName: artistData[dbName].getDict() for dbName in artistData.keys()}
        
        summaryDF = DataFrame(artistDBData)
        return summaryDF
        
        
    def summary(self):
        print("-"*25,self.discname,"-"*25)
        print("-"*10,"DB")
        if len(self.dbdata) == 0:
            print("\t\tNo entries")
        else:
            for source, dbdata in self.dbdata.items():
                dbdata.summary()
        print("-"*10,"Renames")
        if len(self.renames) == 0:
            print("\t\tNo entries")
        else:
            print("\t\t"," ; ".join(self.renames))
        
    def addDBData(self, source, dbdata):
        if self.debug:
            print("  Adding DBData[{0}] for [{1}]".format(source, self.discname))
        self.dbdata[source] = musicDBData(source, self.discname)
        self.dbdata[source].setDBData(dbdata)
        
    def addAlias(self, name):
        self.alias.append(name)
        self.alias = list(set(self.alias))
        
    def addRenames(self, name):
        self.renames.append(name)
        self.renames = list(set(self.renames))