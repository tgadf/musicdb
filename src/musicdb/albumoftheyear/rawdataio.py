""" Raw AlbumOfTheYear Data Storage Class """

__all__ = ["RawDataIO"]

from dbraw import RawDataIOBase
from bs4 import BeautifulSoup
from bs4.element import Tag
from pandas import to_datetime
import regex
import json
from .params import MusicDBParams
from .musicdbid import MusicDBID
from .mediautils import MediaUtils


class RawDataIO(RawDataIOBase):
    def __repr__(self):
        return f"RawDataIO(db={self.db})"
    
    def __init__(self, debug=False):
        super().__init__()
        mdbparams = MusicDBParams()
        self.db = mdbparams.db
        self.aid = MusicDBID()
        self.mutils = MediaUtils()
        self.debug = debug

    ###########################################################################
    # Parse Data
    ###########################################################################
    def getArtistData(self, fid: str, data, ifile) -> 'dict':
        self.bsdata = self.getData(fid, data, ifile)
        assert isinstance(self.bsdata, BeautifulSoup), f"ArtistData [{type(self.bsdata)}] not a BeautifulSoup object"
        self.parseType = "Artist"
                
        nameData    = self.getName()
        urlData     = self.getURL()
        idData      = self.getID(urlData)
        basicData   = self.makeRawBasicData(name=nameData, url=urlData, ID=idData)
        metaData    = self.getMeta()
        infoData    = self.getFileInfo()
        profileData = self.getProfile()
        
        shuffleMediaData = self.getMedia(basicData)
        mediaData        = shuffleMediaData["Media"]
        shuffleData      = shuffleMediaData["Shuffle"]
        
        rawArtistData = self.makeRawArtistData(basic=basicData, profile=profileData, media=mediaData, info=infoData, meta=metaData)
        
        retval = {None: rawArtistData, "ShuffleMedia": shuffleData}
        return retval
        
    ###########################################################################
    # Parse Album Data
    ###########################################################################
    def getAlbumData(self, fid, data, ifile):
        self.bsdata = self.getData(fid, data, ifile)
        assert isinstance(self.bsdata, BeautifulSoup), f"ArtistData [{type(self.bsdata)}] not a BeautifulSoup object"
        retval = {"Album": None}
        
        mediaTypeName = "Album"
        self.parseType = mediaTypeName
        
        ## URL
        urlData  = self.getURL()
        if urlData is None:
            return retval
        url      = urlData.url
        albumID  = self.aid.getAlbumID(urlData.url)
        
        ## Artists
        artistDiv    = self.bsdata.find("div", {"class": "artist"})
        artistRefs   = artistDiv.findAll("a") if isinstance(artistDiv, Tag) else []
        artistData   = [self.getLinkData(ref) for ref in artistRefs]
        albumArtists = []
        for artist in artistData:
            name  = artist.get('Text')
            attr  = artist.get('Attrs')
            href  = attr.get('href') if isinstance(attr, dict) else None
            refID = self.aid.getArtistID(href) if isinstance(href, str) else None
            albumArtists.append((refID,name,href))
        
        
        
        ## Title
        titleDiv  = self.bsdata.find("div", {"class": "albumTitle"})
        titleData = titleDiv.text if isinstance(titleDiv, Tag) else None

        ## Details (Profile)
        profile   = self.getProfile()
        def getReleaseDate(ref):
            if not isinstance(ref, str):
                return None
            vals = [val for val in ref.split("/") if len(val) > 0]
            if len(vals) == 2 and vals[1] == "releases":
                year    = vals[0]
                release = year
            elif len(vals) == 3 and vals[1] == "releases":
                year   = vals[0]
                monday = vals[2].split(".")[0].title()
                release = "-".join([monday,year])
            else:
                release = None
            return release

        releaseInfo = profile.external.get('Links') if isinstance(profile.external, dict) else None
        releaseRef  = releaseInfo[1] if (isinstance(releaseInfo,list) and len(releaseInfo) >= 3) else None
        releaseDate = getReleaseDate(releaseRef)
        try:
            releaseYear = to_datetime(releaseDate).year
        except:
            releaseYear = None
        
        
        userScore   = profile.general.get('UserScore') if isinstance(profile.general, dict) else None
        criticScore = profile.general.get('CriticScore') if isinstance(profile.general, dict) else None
        
        genresList = profile.genres
        genres = [item.get('Text') for item in genresList if isinstance(item, dict)] if isinstance(genresList,list) else None
        genres = genres if (isinstance(genres,list) and len(genres) > 0) else None
        
        tagsList = profile.tags
        tags = [item.get('Text') for item in tagsList if isinstance(item, dict)] if isinstance(tagsList,list) else None
        tags = tags if (isinstance(tags,list) and len(tags) > 0) else None
        
        pageRefsList = profile.extra.get('PageRefs') if isinstance(profile.extra, dict) else None
        pageRefsList = pageRefsList if isinstance(pageRefsList,list) else []
        pageRefs     = []
        for pageRef in pageRefsList:
            name  = pageRef.get('Text')
            attr  = pageRef.get('Attrs')
            href  = attr.get('href') if isinstance(attr, dict) else None
            refID = self.aid.getArtistID(href) if isinstance(href, str) else None
            pageRefs.append((refID,name,href))
        
        
        labelInfo = profile.external.get('Links') if isinstance(profile.external, dict) else None
        labelRef  = [ref for ref in labelInfo if ref.startswith("/label")] if isinstance(labelInfo,list) else None
        labelRef  = labelRef[0] if (isinstance(labelRef,list) and len(labelRef) == 1) else None
        label     = self.detailData.get('Label')
        if isinstance(label,tuple) and len(label) == 2:
            if label[1] is None and isinstance(labelRef, str): 
                label[1] = labelRef
        
            
        ## Tracks (if available)
        trackDiv  = self.bsdata.find("div", {"id": "tracklist"})
        trackTbl  = trackDiv.find("table", {"class": "trackListTable"}) if isinstance(trackDiv, Tag) else None
        trackList = trackTbl.findAll("tr") if isinstance(trackTbl, Tag) else []
        tracks    = []
        for trackRow in trackList:
            trackNumberData = trackRow.find("td", {"class": "trackNumber"})
            trackNumber     = trackNumberData.text if isinstance(trackNumberData, Tag) else None

            trackTitleData  = trackRow.find("td", {"class": "trackTitle"})
            trackLengthData = trackTitleData.find("div", {"class": "length"})
            trackLength     = trackLengthData.text if isinstance(trackLengthData, Tag) else None    
            trackTitleRef   = trackTitleData.find('a') if isinstance(trackTitleData, Tag) else None
            trackTitle      = self.getLinkData(trackTitleRef) if isinstance(trackTitleRef, Tag) else None

            trackRatingData  = trackRow.find("td", {"class": "trackRating"})
            trackRating      = trackRatingData.text if isinstance(trackRatingData, Tag) else None

            tracks.append({"Number": trackNumber, "Title": trackTitle, "Length": trackLength, "Rating": trackRating})

        mediaFormat = self.detailData.get('Format')
        mediaTypeName = mediaFormat if (isinstance(mediaFormat, str) and len(mediaFormat) > 0) else mediaTypeName
            
        mediaID = self.mutils.getMediaID(mediaTypeName, albumID=albumID)
        mediaDeepData = self.makeRawMediaDeepData(mediaID=mediaID, name=titleData, artist=albumArtists, url=url, group=mediaTypeName, tracks=tracks, genres=genres, tags=tags, label=label, pagerefs=pageRefs, userscore=userScore, criticscore=criticScore, year=releaseYear)
        
        return {"Album": mediaDeepData}



    def getName(self):
        h1 = self.bsdata.find("h1", {"class": 'artistHeadline'})
        artistName = h1.text if isinstance(h1,Tag) else None
        if isinstance(artistName, str):
            bracketValues = regex.findall(r'\[(.*?)\]+', artistName)
            if len(bracketValues) > 0:
                ignores = ['rap', '2', '3', '4', 'NOR', 'US', 'unknown Artist', 'CHE', 'email\xa0protected', '70s', '60s', '80s', '90s', 'BRA', 'SWE', 'France', 'FR', 'UK', 'JP', 'DE', 'USA', 'RUS', 'ARG', 'DEU']
                for ignore in ignores:
                    arg = " [{0}]".format(ignore)
                    if arg in artistName:
                        artistName = artistName.replace(arg, "")
                bracketValues = regex.findall(r'\[(.*?)\]+', artistName)
                
            artistName = " & ".join(bracketValues) if len(bracketValues) > 0 else artistName
            anc = self.makeRawNameData(name=artistName, err=None)
            return anc
        else:
            script = self.bsdata.find("script", {"type": "application/ld+json"})
            if script is None:
                metaurl   = self.bsdata.find("meta", {"property": "og:url"})
                url = metaurl.attrs['content'] if isinstance(metaurl,Tag) else None
                print(self.getFileID())
                print(self.getFileInfo())
                raise ValueError(f"Could not find Artist Name from {metaurl}")

            try:
                artist = json.loads(script.contents[0])["name"]
            except:
                metaurl   = self.bsdata.find("meta", {"property": "og:url"})
                url = metaurl.attrs['content'] if isinstance(metaurl,Tag) else None
                print(self.getFileID())
                print(self.getFileInfo())
                raise ValueError(f"Could not find Artist Name from {metaurl}")

            artistName = artist
            bracketValues = regex.findall(r'\[(.*?)\]+', artistName)
            if len(bracketValues) > 0:
                ignores = ['rap', '2', '3', '4', 'NOR', 'US', 'unknown Artist', 'CHE', 'email\xa0protected', '70s', '60s', '80s', '90s', 'BRA', 'SWE', 'France', 'FR', 'UK', 'JP', 'DE', 'USA', 'RUS', 'ARG', 'DEU']
                for ignore in ignores:
                    arg = " [{0}]".format(ignore)
                    if arg in artistName:
                        artistName = artistName.replace(arg, "")
                bracketValues = regex.findall(r'\[(.*?)\]+', artistName)
                
            artistName = " & ".join(bracketValues) if len(bracketValues) > 0 else artistName
            anc = self.makeRawNameData(name=artistName, err=None)
            return anc

    

    ###########################################################################################################################
    ## Meta Information
    ###########################################################################################################################
    def getMeta(self):
        metatitle = self.bsdata.find("meta", {"property": "og:title"})
        title = metatitle.attrs['content'] if isinstance(metatitle,Tag) else None
        assert isinstance(title, str), f"Could not get title from meta [{metatitle}]"
        
        metaurl   = self.bsdata.find("meta", {"property": "og:url"})
        url = metaurl.attrs['content'] if isinstance(metaurl,Tag) else None
        assert isinstance(url, str), f"Could not get url from meta [{metatitle}]"
        
        amc = self.makeRawMetaData(title=title, url=url)
        return amc
        

    ###########################################################################################################################
    ## Artist URL
    ###########################################################################################################################
    def getURL(self):
        urlTag = self.bsdata.find("meta", {"property": "og:url"})
        if not isinstance(urlTag,Tag):
            return None
        
        url = urlTag.get("content")
        assert isinstance(url, str), f"Could not get url from meta og:url [{urlTag}]"
            
        auc = self.makeRawURLData(url=url)
        return auc

    

    ###########################################################################################################################
    ## Artist ID
    ###########################################################################################################################
    def getID(self, urlData):
        artistID = self.aid.getArtistID(urlData.url)
        aic = self.makeRawIDData(ID=artistID)
        return aic
    
    

    ###########################################################################################################################
    ## Artist Variations
    ###########################################################################################################################
    def getProfile(self):      
        generalData  = {}
        genreData    = {}
        extraData    = {}
        externalData = {}
        tagsData     = {}
        
        artistInfo = self.bsdata.find("div", {"class": f"{self.parseType.lower()}TopBox info"})
        artistInfoRefs = artistInfo.findAll("a") if isinstance(artistInfo,Tag) else []
        detailRows = artistInfo.findAll("div", {"class": "detailRow"}) if isinstance(artistInfo,Tag) else []
        
        genreRefs    = []
        tagRefs      = []
        externalRefs = []
        for ref in artistInfoRefs:
            href = ref.get('href')
            if href.startswith("/genre/") or "?genre=" in href:
                genreRefs.append(ref)
            elif href.startswith("/tag/"):
                tagRefs.append(ref)
            elif href in ["#", "/account/"]:
                continue
            else:
                externalRefs.append(ref)
                
                
        ##################################################################################################################
        # Genre Data
        ##################################################################################################################
        if self.parseType == "Artist":
            genreLinksData = [self.getLinkData(ref) for ref in genreRefs]
            genreTextData  = [linkData['Text'] for linkData in genreLinksData]
            genreData      = genreTextData if len(genreTextData) > 0 else None
        elif self.parseType == "Album":
            genreData = [self.getLinkData(ref) for ref in genreRefs if "?genre=" in ref.attrs['href']]
            genreData = genreData if len(genreData) > 0 else None
        else:
            raise ValueError(f"Media Type [{self.parseType}] has no genre available")
        
        
        ##################################################################################################################
        # Tag Data
        ##################################################################################################################
        tagLinksData = [self.getLinkData(ref) for ref in tagRefs]
        tagsData = [linkData['Text'] for linkData in tagLinksData] if len(tagLinksData) > 0 else None
        

        ##################################################################################################################
        # Website/Twitter Data
        ##################################################################################################################
        
        externalData    = {"Links": [ref.get('href').replace("//", "") for ref in externalRefs]} if len(externalRefs) > 0 else None
        self.detailData = {}
        for row in detailRows:
            span = row.find("span")
            if isinstance(span,Tag):
                key   = span.text.strip()
                key   = key[1:].strip() if (isinstance(key, str) and key.startswith("/")) else key
                ref   = row.find('a')
                ref   = ref.get('href') if isinstance(ref,Tag) else None
                span.decompose()
                value = row.text.strip()
                value = None if (isinstance(value, str) and len(value) == 0) else value
                self.detailData[key] = (value,ref)
            
            
            
        ##################################################################################################################
        # User/Critic Score Data
        ##################################################################################################################
        userScoreDiv   = self.bsdata.find("div", {"class": f"{self.parseType.lower()}UserScore"})
        userScore      = userScoreDiv.text.strip() if isinstance(userScoreDiv, Tag) else None
        userScore      = int(userScore) if (isinstance(userScore, str) and userScore.isdigit()) else None
        generalData["UserScore"] = userScore
        criticScoreDiv = self.bsdata.find("div", {"class": f"{self.parseType.lower()}CriticScore"})
        criticScore    = criticScoreDiv.text.strip() if isinstance(criticScoreDiv, Tag) else None        
        criticScore    = int(criticScore) if (isinstance(criticScore, str) and criticScore.isdigit()) else None
        generalData["CriticScore"] = criticScore

        
        ##################################################################################################################
        # Related
        ##################################################################################################################
        if self.parseType == "Artist":
            relatedArtists = self.bsdata.find("div", {"class": "relatedArtists"})
            artistBlocks   = relatedArtists.findAll("div", {"class": "artistBlock"}) if relatedArtists is not None else None
            refs           = [artistBlock.find("a") for artistBlock in artistBlocks] if artistBlocks is not None else None
            if isinstance(refs,list) and len(refs) > 0:
                extraData["RelatedArtists"] = []
                for ref in refs:
                    refimg   = ref.find("img")
                    refName  = refimg.get('alt') if isinstance(refimg,Tag) else None
                    linkData = self.getLinkData(ref)
                    refData  = {"Name": refName, "URL": linkData['Attrs']['href']}
                    extraData["RelatedArtists"].append(refData)
        elif self.parseType == "Album" and False:
            refs = [ref for ref in self.bsdata.findAll("a") if ref.get('href', '').startswith("/artist/")]
            pageRefs = {ref.attrs['href']: self.getLinkData(ref) for ref in refs if ref.text not in ["View All", "More Albums"]}
            if isinstance(pageRefs, dict) and len(pageRefs) > 0:
                extraData["PageRefs"] = list(pageRefs.values())
                
                
        generalData = generalData if len(generalData) > 0 else None
                
        apc = self.makeRawProfileData(general=generalData, genres=genreData, tags=tagsData, extra=extraData, external=externalData)
        return apc

    
    
    ###########################################################################################################################
    ## Artist Media
    ########################################################################################################################### 
    def getMedia(self, basic):
        artistID = basic.id
        
        mediaCollection = {}
        shuffleData     = {}
        
        albumBlocks = self.bsdata.findAll("div", {"class": "albumBlock"})
        #print(f"Blocks: {len(albumBlocks)}")
        for i,albumBlock in enumerate(albumBlocks):
            #print(albumBlock)
            #print(i,'/',len(albumBlocks))
            blockData = {}
            for div in albumBlock.findAll("div"):
                attr = div.attrs.get("class")
                key  = attr[0] if isinstance(attr,list) else None
                ref  = div.find("a")
                val  = self.getLinkData(ref) if ref is not None else self.getTextData(div)
                blockData[key] = val

            urlData = blockData.get("image")            
            url     = urlData['Attrs']['href'] if isinstance(urlData, dict) else None

            title = blockData.get("albumTitle")
            title = title if isinstance(title, str) else None

            yearData = blockData.get("date")
            year = yearData if isinstance(yearData, str) else None            
            try:
                year = to_datetime(year).year
            except:
                year = None

            albumID = self.aid.getAlbumID(url)
            mediaTypeData = blockData.get("type")
            mediaTypeDataValues = None
            if isinstance(mediaTypeData, str) and "•" in mediaTypeData:
                mediaTypeDataValues = mediaTypeData.split("•")
            elif isinstance(mediaTypeData, str) and "â€¢" in mediaTypeData:
                mediaTypeDataValues = mediaTypeData.split("â€¢")
                
            if isinstance(mediaTypeDataValues,list) and len(mediaTypeDataValues) > 2:
                mediaTypeName = mediaTypeDataValues[0].strip()
                mediaArtists  = (basic.id,basic.name,", ".join([value.strip() for value in mediaTypeDataValues[1:]]))
                #print('==>',mediaTypeName,'\t',mediaArtists)
            elif isinstance(mediaTypeDataValues,list) and len(mediaTypeDataValues) == 2:
                mediaTypeName = mediaTypeDataValues[0].strip()
                mediaArtists  = (basic.id,basic.name,mediaTypeDataValues[1].strip())
                #print('==>',mediaTypeName,'\t',mediaArtists)
            elif isinstance(mediaTypeDataValues,list) and len(mediaTypeDataValues) == 1:
                mediaTypeName = mediaTypeData.strip()
                mediaArtists  = (basic.id,basic.name,None)
                #print('-->',mediaTypeName,'\t',mediaArtists)
            else:
                mediaTypeName = mediaTypeData
                mediaArtists  = (basic.id,basic.name,None)
            
            #print('| ',mediaTypeData,' | ',mediaTypeName,' | ',albumID,' | ',title,' |',url,' |')
            
            if not all([isinstance(value, str) for value in [mediaTypeName,albumID,title]]):
                continue

            mediaID = self.mutils.getMediaID(mediaTypeName, artistID=artistID, albumID=albumID)
            mediaRootData = self.makeRawMediaRootData(mediaID=mediaID, name=title)
            mediaDeepData = self.makeRawMediaDeepData(mediaID=mediaID, name=title, artist=mediaArtists, url=url, group=mediaTypeName, year=year)
            
            if mediaCollection.get(mediaTypeName) is None:
                mediaCollection[mediaTypeName] = []
            mediaCollection[mediaTypeName].append(mediaRootData)
            shuffleData[mediaID] = mediaDeepData
            
            
        mediaData   = self.makeRawMediaCollectionData()
        for mediaTypeName,mediaTypeData in mediaCollection.items():
            mediaData.add(mediaTypeName, mediaTypeData)
            
        return {"Media": mediaData, "Shuffle": shuffleData}