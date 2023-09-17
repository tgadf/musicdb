""" Raw AlbumOfTheYear Data I/O """

__all__ = ["RawWebData"]

from utils import WebIO, WebData, HTMLIO
from urllib.parse import quote
import json
from bs4 import BeautifulSoup, element


class RawWebData(WebIO):
    def __repr__(self):
        return f"RawWebData(name={self.name}, baseurl={self.baseURL})"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "AlbumOfTheYear"
        self.baseURL = "https://www.albumoftheyear.org"
        
        if self.verbose is True:
            print("{0} Web I/O".format(self.name))
            
    
    ####################################################################################################################################
    # Basic Artist Search Website Data
    ####################################################################################################################################
    def getArtistSearchURL(self, artistName):
        qName = quote(artistName)
        return f"{self.baseURL}/search/artists/?q={qName}"
    
    def getArtistSearchData(self, artistName):
        print("Searching For {0: <50}".format(artistName), end="")
        response      = self.get(self.getArtistSearchURL(artistName))
        result        = response if isinstance(response, WebData) else None
        code          = result.code
        data          = result.data
        status        = code == 200
        if status is False:
            return None
    
        bsdata = HTMLIO().get(data)
        content = bsdata.find("div", {"id": "centerContent"})
        artistRefs = {}
        if isinstance(content, element.Tag):
            refs = [ref for ref in content.findAll("a") if ref.attrs['href'].startswith("/artist/")]
            artists = [ref for ref in refs if not isinstance(ref.find("img"), element.Tag)]
            artistRefs = {ref.attrs['href']: ref.text for ref in artists}
        retval = artistRefs

        print(len(retval))
        return retval
    
    
    ####################################################################################################################################
    # Basic Artist Website Data
    ####################################################################################################################################
    def getArtistURL(self, artistRef):
        return f"{self.baseURL}{artistRef}?type=all"
    
    def getArtistData(self, artistName, artistRef):
        artistVal = f"{artistName} ({artistRef})"
        print(f"Getting Artist Data For {artistVal: <120}   ", end="")
        response      = self.get(self.getArtistURL(artistRef))
        result        = response if isinstance(response, WebData) else None
        code          = result.code
        data          = result.data
        status        = code == 200
        print(status)
        if status is False:
            return None
        return data
    
    
    ####################################################################################################################################
    # Basic Album Search Website Data
    ####################################################################################################################################
    def getAlbumURL(self, albumRef):
        return f"{self.baseURL}{albumRef}"
    
    def getAlbumData(self, albumName, albumRef):
        albumVal = f"{albumName} ({albumRef})"
        print(f"Getting Album Data For {albumVal: <120}   ", end="")
        response      = self.get(self.getAlbumURL(albumRef))
        result        = response if isinstance(response, WebData) else None
        code          = result.code
        data          = result.data
        status        = code == 200
        print(status)
        if status is False:
            return None
        return data