""" Utility Classes """

__all__ = ["MediaUtils"]

from dbraw import RawDataIOBase
from .params import MusicDBParams


###############################################################################
# ModVal Data Classes
###############################################################################
class MediaUtils:
    def __repr__(self):
        return f"MediaUtils(db={self.db})"
    
    def __init__(self, unique=False):
        self.unique = unique
        self.rdbio = RawDataIOBase()
        mdbparams = MusicDBParams()
        self.mediaTypes = mdbparams.mediaTypes
        assert isinstance(self.mediaTypes, list), f"MediaTypes must be a list [{type(self.mediaTypes)}]"
        
    def getMediaID(self, mediaTypeName, artistID=None, albumID=None, trackID=None):
        if mediaTypeName not in self.mediaTypes:
            print(f"\"{mediaTypeName}\", ")
        if isinstance(artistID, str):
            mediaIDTypes = [artistID, albumID]
        else:
            mediaIDTypes = [albumID]
        assert all([isinstance(value, str) for value in mediaIDTypes]), f"Requires string values for [artistID={artistID}, albumID={albumID}, trackID={trackID}]"
        mediaID = "-".join(mediaIDTypes)
        return mediaID
    
    def compareMedia(self, mediaOld, mediaNew):
        assert all([self.rdbio.isRawMediaDeepData(obj) for obj in [mediaOld, mediaNew]]), f"Can only compare media if both are MediaDeepData [{type(mediaOld)} / {type(mediaNew)}]"
        mediaTypeName = mediaOld.group
        assert mediaTypeName in self.mediaTypes, f"MediaTypeName [{mediaTypeName}] not in allowed list {self.mediaTypes}"
        mediaTypeDataDict = {"ShuffleArtist": ["name"], "Album": ["name", "artist"], "ShuffleAlbum": ["name", "artist"], "ShuffleTrack": ["name", "artist", "url", "album", "duration"]}
        mediaOldCompareDict = {k: v for k, v in mediaOld.get().items() if k in mediaTypeDataDict[mediaTypeName]}
        mediaNewCompareDict = {k: v for k, v in mediaNew.get().items() if k in mediaTypeDataDict[mediaTypeName]}
        if mediaOldCompareDict == mediaNewCompareDict:
            retval = True
        else:
            if self.unique is True:
                retval = False
            else:
                retval = True
                
        return retval