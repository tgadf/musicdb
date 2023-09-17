""" DBID Store For Easy Access """

__all__ = ["IDStore"]

from dbmaster import MasterDBs
from importlib import import_module


###########################################################################################################################
# Music DB ID Gate
###########################################################################################################################
class IDStore:
    def __init__(self, **kwargs):
        self.verbose = kwargs.get('verbose', False)
        mdbs = MasterDBs()
        ios = {db: getattr(import_module('musicdb.{0}'.format(db.lower())), "MusicDBID") for db in mdbs.getDBs()}
        self.ios = {db: dbid() for db,dbid in ios.items()}
        for db,dbid in self.ios.items():
            exec("self.get{0}ID = dbid.get".format(db))
            exec("self.get{0}id = dbid.get".format(dbid.short))
        
    def get(self, db, s):
        return self.ios[db].get(s)