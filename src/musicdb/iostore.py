""" MusicDBIO Store For Easy Access """

__all__ = ["getdbio", "getdbios"]

from dbmaster import MasterDBs
from importlib import import_module
import inspect


def getdbio(db: str, **kwargs):
    verbose = kwargs.get('verbose', False)
    dbmod = db.lower()
    
    try:
        impmod = import_module(f"musicdb.{db.lower()}")
        mdbio = getattr(impmod, "MusicDBIO") if hasattr(impmod, "MusicDBIO") else None
        if inspect.isclass(mdbio) is True:
            return mdbio(**kwargs)
    except Exception as error:
        if verbose is True:
            print(f"Could not load db [{db}]: {error}")

    return None


def getdbios(**kwargs):
    ios = {db: getdbio(db, **kwargs) for db in MasterDBs().getDBs()}
    ios = {db: dbio for db, dbio in ios.items() if dbio is not None}
    return ios