""" Classes to get db artist mod value """

__all__ = ["ParseRawData"]
         
from master import MasterParams, MasterBasic
from base import MusicDBBaseData, MusicDBBaseDirs, RawDataBase
from utils import ParseRawDataUtils
from dbid import MusicDBIDModVal
from timeutils import Timestat
from ioutils import FileIO
from listUtils import getFlatList
from pandas import concat, Series
from numpy import array_split
from .rawdbdata import RawDBData

        
class ParseRawData:
    def __init__(self, mdbdata, mdbdir, **kwargs):
        if not isinstance(mdbdata, MusicDBBaseData):
            raise ValueError("ParseRawData(mdbdata) is not of type MusicDBBaseData")
        if not isinstance(mdbdir, MusicDBBaseDirs):
            raise ValueError("ParseRawData(mdbdir) is not of type MusicDBBaseDirs")
        self.rawio     = RawDBData()
        self.mdbdir    = mdbdir
        self.mdbdata   = mdbdata
        self.prdutils  = ParseRawDataUtils(mdbdata, mdbdir, self.rawio, **kwargs)
        self.fileTypes = ["Artist", "Album"]
        self.verbose   = kwargs.get('debug', kwargs.get('verbose', False))
        self.db        = mdbdir.db
        self.badData   = {}
        self.mv        = MusicDBIDModVal()
        
    def parse(self, modVal, expr='< 0 Days', force=False, **kwargs):
        keys = self.fileTypes
        parse = {key: True for key in keys} 
        if kwargs.get('parse') is not None:
            assert kwargs['parse'] in keys, f"parse argument must be {keys}"
            parse = {key: False for key in keys}
            parse[kwargs['parse']] = True

        for key,value in parse.items():
            if value is True: 
                exec(f"self.parse{key}Data(modVal, expr, force)")

        
    #####################################################################################################################
    # Parse Album Data
    #####################################################################################################################
    def parseArtistData(self, modVal, expr='< 0 Days', force=False):
        fileType = "Artist"
        subFileTypes = {f"{sfType}s": sfType for sfType in ["Artist", "Album"]}
        if self.verbose: ts = Timestat("Parsing ModVal={0} Raw {1} {2} Files(expr=\'{3}\', force={4})".format(modVal, fileType, self.db, expr, force))
                
                
        ############################################
        # New Files Since Last ModValData Update
        ############################################
        io = FileIO()
        newFiles = self.prdutils.getNewFiles(modVal, fileType=fileType, tsFileType=f"Search{fileType}Base", expr=expr, force=force)
            
        N = len(newFiles)
        if N > 0:
            ############################################
            # Current ModValData
            ############################################
            modValData = {sfType: {} for sfType in subFileTypes.keys()}
            #modValData = self.prdutils.getFileTypeModValData(modVal, fileType, force)
            if self.verbose: print("  ===> Found {0} Previously Saved {1} ModVal Data Entries".format(len(modValData), fileType))

            ############################################
            # Loop Over Files And Save Results
            ############################################
            newData = {sfType: 0 for sfType in subFileTypes.keys()}
            badData = {sfType: 0 for sfType in subFileTypes.keys()}
            if self.verbose: tsParse = Timestat("Parsing {0} New {1} Files".format(N, fileType))
            pModVal = self.prdutils.getPrintModValue(N)
            for i,ifile in enumerate(newFiles):
                if (i+1) % pModVal == 0 or (i+1) == pModVal/2:
                    if self.verbose: tsParse.update(n=i+1, N=N)

                globData = io.get(ifile)
                for fid,fdata in globData.items():
                    rData = eval(f"self.rawio.get{fileType}Data(fdata)")
                    
                    ###################### Artists ######################
                    subFileType = "Artists"
                    sfType = subFileType
                    subFileTypeData = rData.get(subFileType)
                    try:
                        artistID = subFileTypeData.ID.ID
                    except:
                        artistID = None
                    if isinstance(artistID, str):
                        newData[subFileType] += 1
                        trueModVal = self.mv.get(artistID)
                        if modValData[sfType].get(trueModVal) is None:
                            modValData[sfType][trueModVal] = {}
                        modValData[sfType][trueModVal][artistID] = subFileTypeData
                    else:
                        badData[subFileType] += 1
                    
                    
                    ###################### Albums ######################
                    subFileType = "Albums"
                    sfType = subFileType
                    subFileTypeData = rData.get(subFileType)
                    for mediaID,mediaData in rData[sfType].items():
                        if isinstance(mediaID,str):
                            newData[sfType] += 1
                            trueModVal = self.mv.get(mediaID)
                            if modValData[sfType].get(trueModVal) is None:
                                modValData[sfType][trueModVal] = {}
                            modValData[sfType][trueModVal][mediaID] = mediaData
                        else:
                            badData[sfType] += 1
                        
            if self.verbose: tsParse.stop()

            for sfType,subFileType in subFileTypes.items():
                if newData[sfType] > 0:
                    numModValData = sum([len(trueModValData.values()) for trueModVal,trueModValData in modValData[sfType].items()])
                    numNewData    = newData[sfType]
                    numBadData    = badData[sfType]
                    if self.verbose: print(f"  ===> Saving [{numModValData}/{numNewData}/{numBadData}] ModVal={modVal} {sfType} DB Data Entries")
                    for i,(trueModVal,trueModValData) in enumerate(modValData[sfType].items()):
                        subFileTypeName = f"Search{subFileType}"
                        key = f"{self.db}-{subFileTypeName}-mv-{trueModVal}-gv-{modVal}"
                        
                        filename = eval(f"self.mdbdata.getModVal{subFileTypeName}Filename(trueModVal, key)")
                        if (i+1) % 25 == 0 or (i+1) == 5:
                            if self.verbose: print(f"\t  ===> TrueModVal={trueModVal: <4}  ModVal={modVal: <4}   i={i: <4}   Data={len(trueModValData)}")
                        io.save(idata=trueModValData, ifile=filename)
                else:
                    if self.verbose: print(f"  ===> Did not find any new data from {sfType} type data")   
        
        if self.verbose: ts.stop()
        

    #####################################################################################################################
    # Primary Album Parser
    #####################################################################################################################
    def parseAlbumData(self, modVal, expr='< 0 Days', force=False):
        fileType = "Album"
        if self.verbose: ts = Timestat("Parsing ModVal={0} Raw {1} {2} Files(expr=\'{3}\', force={4})".format(modVal, fileType, self.db, expr, force))
                
                
        ############################################
        # New Files Since Last ModValData Update
        ############################################
        io = FileIO()
        newFiles = self.prdutils.getNewFiles(modVal, fileType=fileType, expr=expr, force=force, tsFileType=fileType)
            
        N = len(newFiles)
        if N > 0:
            ############################################
            # Current ModValData
            ############################################
            modValData = self.prdutils.getFileTypeModValData(modVal, fileType=fileType, force=force)
            if self.verbose: print("  ===> Found {0} Previously Saved {1} ModVal Data Entries".format(len(modValData), fileType))

            ############################################
            # Loop Over Files And Save Results
            ############################################
            newData = 0
            badData = 0
            if self.verbose: tsParse = Timestat(f"Parsing {N} New {fileType} Files")
            pModVal = self.prdutils.getPrintModValue(N)
            for i,ifile in enumerate(newFiles):
                if (i+1) % pModVal == 0 or (i+1) == pModVal/2:
                    if self.verbose: tsParse.update(n=i+1, N=N)

                globData = io.get(ifile)
                for fid,fdata in globData.items():
                    cmd   = "self.rawio.get{0}Data(fdata)".format(fileType)
                    rData = eval(cmd)
                    if isinstance(rData.code, str):
                        newData += 1
                        modValData[rData.code] = rData
                    else:
                        print(f"{fid}  {ifile}")
                        badData += 1


            if self.verbose: tsParse.stop()

            if newData > 0:
                if self.verbose: print(f"  ===> Saving [{newData}/{len(modValData)}/{badData}] DB Data Entries")
                self.prdutils.saveFileTypeModValData(modVal, fileType, modValData)
            else:
                if self.verbose: print(f"  ===> Did not find any new data from {N} files")
                
        
        if self.verbose: ts.stop()

        
    #####################################################################################################################
    # Merge Sub Artist Data
    #####################################################################################################################
    def mergeModValArtistData(self, modVal=None, **kwargs):
        fileType     = "Artist"
        mb           = MasterBasic()
        modVals      = mb.getModVals(listIt=True) if modVal is None else [modVal]
        self.verbose = kwargs.get('verbose', False) if kwargs.get('verbose') is not None else self.verbose
        if self.verbose: ts = Timestat(f"Creating {len(modVals)} {fileType} ModVal Data")

        io = FileIO()
        for n,modVal in enumerate(modVals):
            if self.verbose is True and ((n+1) % 25 == 0 or (n+1) == 5):
                ts.update(n=n+1,N=len(modVals))

            modValData = {}
            files = self.mdbdir.getModValSearchArtistDataDir(modVal).glob("*.p", debug=False)
            for ifile in files:
                subModValData = io.get(ifile)
                for artistID,artistIDData in subModValData.items():
                    if modValData.get(artistID) is None:
                        modValData[artistID] = artistIDData
                    else:
                        for mediaType,mediaTypeData in artistIDData.media.media.items():
                            if isinstance(modValData[artistID].media.media.get(mediaType),dict):
                                modValData[artistID].media.media[mediaType].update(mediaTypeData)
                            else:
                                modValData[artistID].media.media[mediaType] = mediaTypeData
                        
            self.prdutils.saveFileTypeModValData(modVal, f"Search{fileType}Base", modValData)
            
        if self.verbose: ts.stop()            

        
    #####################################################################################################################
    # Merge Sub Album / Song Data
    #####################################################################################################################
    def mergeModValMediaData(self, modVal=None, fileType=None, **kwargs):
        if fileType not in ["Album"]:
            raise ValueError(f"FileType [{fileType}] is not allowed")
        mb           = MasterBasic()
        modVals      = mb.getModVals(listIt=True) if modVal is None else [modVal]
        verbose = kwargs.get('verbose', False) if kwargs.get('verbose') is not None else self.verbose
        if verbose: ts = Timestat(f"Creating {len(modVals)} {fileType} ModVal Data")

        io = FileIO()

        numNewTotal = (0,0)
        for n,modVal in enumerate(modVals):
            if self.verbose is True and ((n+1) % 25 == 0 or (n+1) == 5):
                ts.update(n=n+1,N=len(modVals))
        
            files = eval(f"self.mdbdir.getModValSearch{fileType}DataDir(modVal).glob('*.p', debug=False)")
            modValData = concat([Series(io.get(ifile)) for ifile in files])
            modValData = modValData[~modValData.index.duplicated()]  ## There will be a lot of duplicates because we download by artist, not media
            try:
                mediaModValData = eval(f"self.mdbdata.getModVal{fileType}Data(modVal)")
                matched         = mediaModValData[mediaModValData.index.isin(modValData.index)]
                unmatched       = modValData[~modValData.index.isin(matched.index)]
                mergedData      = concat([matched,unmatched])
                numNewMedia     = (len(matched),len(mergedData))
            except:
                mediaModValData = None
                mergedData      = modValData
                numNewMedia     = (0,len(mergedData))
                            
            numNewTotal = (numNewTotal[0] + numNewMedia[0], numNewTotal[1] + numNewMedia[1])
            if numNewMedia[1] > 0:
                if verbose: print(f"  ==> Merged {fileType} Data For {numNewMedia[0]}/{numNewMedia[1]} ModVal={modVal} Media. Saving Data ... ", end="")
                self.prdutils.saveFileTypeModValData(modVal, f"Search{fileType}Base", mergedData)
                if verbose: print("Done.")
            else:
                if verbose: print(f"Did not find any {fileType} record matches...")
        ts.stop()

        numNewMedia = numNewTotal
        if verbose: print(f"Merged {fileType} Data For {numNewTotal[0]}/{numNewTotal[1]} Media. Saving Data ... ", end="")
        if self.verbose: ts.stop()            

        
    #####################################################################################################################
    # Merge Parsed Data
    #####################################################################################################################   
    def mergeData(self, **kwargs):
        self.mergeModValArtistData(**kwargs)
        self.mergeModValMediaData(fileType='Album', **kwargs)
        self.mergeModValData()
        
        
    def mergeModValData(self, modVal=None, **kwargs):
        mb             = MasterBasic()
        modVals        = mb.getModVals(listIt=True) if modVal is None else [modVal]

        rdb            = RawDataBase()            
        verbose        = kwargs.get('verbose', False) if kwargs.get('verbose') is not None else self.verbose
        numModsArtist  = kwargs.get('numModsArtist', 4)
        mergeArtists   = kwargs.get('mergeArtists', False)
        modValsArtists = array_split(modVals, min([len(modVals),numModsArtist]))

        numModsAlbum  = kwargs.get('numModsAlbum', 2)
        mergeAlbums   = kwargs.get('mergeAlbums', False)
        try:
            modValsAlbums = array_split(range(100), numModsAlbum)
        except:
            modValsAlbums = []
        
        
        if mergeArtists is True:
            ts = Timestat(f"Merging Primary Artist Data")
            self.mergeModValArtistData(**kwargs)
            ts.stop()
            
        if mergeAlbums is True:
            ts = Timestat(f"Merging Primary Album Media Data")
            self.mergeModValMediaData(fileType='Album', **kwargs)
            ts.stop()

        tsArtist = Timestat(f"Merging Artist <=> Media Data Using {len(modValsArtists)} Mod Groups")
        
        for i,modValsArtist in enumerate(modValsArtists):
            artistData = concat([self.mdbdata.getModValSearchArtistBaseData(modVal) for modVal in modValsArtist])

            if len(modValsAlbums) > 0:
                tsAlbum = Timestat(f"Merging Albums Data For {len(artistData)} Artists Using {len(modValsAlbums)} Mod Groups", ind=2)
                for nm,modValsAlbum in enumerate(modValsAlbums):
                    albumData = concat([self.mdbdata.getModValSearchAlbumBaseData(modVal) for modVal in modValsAlbum])

                    for n,(artistID,artistIDData) in enumerate(artistData.iteritems()):
                        for mediaType in artistIDData.media.media.keys():
                            artistIDData.media.media[mediaType] = {code: albumData.get(code, album) for code,album in artistIDData.media.media.get(mediaType, {}).items()}
                        #artistIDData.media.media["Albums"] = {code: albumData.get(code, album) for code,album in artistIDData.media.media.get('Albums', {}).items()}
                    tsAlbum.update(n=nm+1, N=len(modValsAlbums))

                    del albumData
                tsAlbum.stop()

            tsArtist.update(n=i+1, N=numModsArtist)
            
            tsSaving = Timestat(f"Saving {len(modValsArtist)} Merged Artists Data")
            for modVal in modValsArtist:
                modValData = artistData[artistData.index.map(self.mv.get) == modVal]
                print(f" ===> Saving {len(modValData): >7} Artists For ModVal={modVal}")
                self.prdutils.saveModValData(modVal, modValData)
            print("\n")
            tsSaving.stop()
            
        tsArtist.stop()