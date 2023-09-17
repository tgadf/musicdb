""" AlbumOfTheYear Music DB ID """

__all__ = ["MusicDBID"]

from dbbase import MusicDBIDBase


class MusicDBID(MusicDBIDBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        patterns = [r'https://www.albumoftheyear.org/artist/([\d]+)-([^/?]+)']
        patterns += [r'https://www.albumoftheyear.org/artist/([\d]+)']
        patterns += [r'/artist/([\d]+)-([^/?]+)']
        patterns += [r'artist/([\d]+)-([^/?]+)']
        patterns += [r'/artist/([\d]+)']
        patterns += [r'artist/([\d]+)']
        patterns += [r'([\d]+)']
        self.patterns = patterns
        self.get = self.getArtistID
        self.short = "aoty"
        
        album_patterns = [r'https://www.albumoftheyear.org/album/([\d]+)-([^/?]+)']
        album_patterns += [r'https://www.albumoftheyear.org/album/([\d]+)']
        album_patterns += [r'/album/([\d]+)-([^/?]+)']
        album_patterns += [r'album/([\d]+)-([^/?]+)']
        self.album_patterns = album_patterns

    def getArtistID(self, s):
        self.s = str(s)
        return self.getArtistIDFromPatterns(self.s, self.patterns)
    
    def getAlbumID(self, s, **kwargs):
        self.s = str(s)
        return self.getArtistIDFromPatterns(self.s, self.album_patterns)