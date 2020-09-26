class musicDBData:
    def __init__(self, source, artist):
        self.artist    = artist
        self.source    = source
        self.dbdata    = {}
        self.music     = []
        
        self.debug = False
        
    def summary(self):
        print("-"*10,self.source)
        for db in sorted(self.dbdata.keys()):
            dbID = self.dbdata[db]
            if isinstance(dbID, dict):
                tmp = dbID.get("ID")
                if tmp is not None:
                    try:
                        dbID = int(tmp)
                    except:
                        dbID = "NotIntFromDict"
                else:
                    dbID = "NoneFromNone"
            elif isinstance(dbID, str):
                tmp = dbID
                try:
                    dbID = int(tmp)
                except:
                    dbID = "NotIntFromStr"
            print("\t\t","\t{0: <25}{1}".format(db,dbID))
        print("\t\t","\t{0: <25}{1}".format("Music",len(self.music)))
        
    def addMusic(self, music):
        for item in music:
            self.music.append(item)
        
    def setDBIDData(self, db, dbID):
        if self.dbdata.get(db) is None:
            if self.debug:
                print("      Setting DBID[{0}] for DB[{1}].".format(dbID, db))
            self.dbdata[db] = dbID
        else:
            if dbID != self.dbdata[db]:
                raise ValueError("Chart IDs for DB {0} do not match!".format(dbID, self.dbdata[db]))
                
    def setDBData(self, dbdata):
        if self.debug:
            print("    Adding DBData[{0}] for [{1}]. Total of {2} items".format(self.source, self.artist, len(dbdata)))
        for db, dbID in dbdata.items():
            if self.debug:
                print("      Adding DBID[{0}] for DB[{1}].".format(dbID, db))
            self.setDBIDData(db, dbID)