def searchForMutualArtistDBEntries(mdb, artistName, num=2, cutoff=0.8, debug=[None]):
    retval     = {}

    
    ######################################################################
    #### Determine Albums To Match
    ######################################################################
    artistAlbums = []
    dbsToMatch   = []
    dbMatches    = mdb.getArtistDataIDs(artistName)
    knownDBs     = []
    for db,artistID in dbMatches.items():
        if artistID is not None:
            artistAlbums.append(mdb.getArtistAlbumsFromID(db, artistID, flatten=True))
            knownDBs.append(db)
        else:
            dbsToMatch.append(db)
    from listUtils import getFlatList
    knownArtistAlbums   = list(set(getFlatList(artistAlbums)))
    print("Searching for matches:  [{0}] using [{1}] albums collected from [{2}] dbs".format(artistName, len(knownArtistAlbums), len(artistAlbums)))
    print("  Will search for matches in these DBs: {0}".format(dbsToMatch))
    
    
    ######################################################################
    #### Loop Over Missing DBs
    ######################################################################
    for db in dbsToMatch:
        
        artistDBIDs = mdb.getArtistDBIDs(artistName, db, cutoff=0.7, num=10, debug=False)
        print("{0: <20}".format(db), end="\t")
        if "Full" in debug:
            print("Found {0} possible artists in DB".format(len(artistDBIDs)))
        else:
            print("")
        
        
        
        
        ######################################################################
        #### Search For Matches in Possible IDs
        ######################################################################
        resultD = {"ID": None, "Matches": num, "Score": 0.0, "Best": None}
        for dbArtistName, dbArtistIDs in artistDBIDs.items():
            for dbArtistID in dbArtistIDs:
                dbArtistIDAlbums = mdb.getArtistAlbumsFromID(db, dbArtistID, flatten=True)
                                
                ma = matchAlbums()
                ma.match(knownArtistAlbums, dbArtistIDAlbums)
                if "ID" in debug or "Full" in debug:
                    print("\t\t{0: <45}{1}\t{2}\t{3}\t{4}".format(dbArtistID, len(dbArtistIDAlbums), ma.near, ma.score, ma.maxval))
                if ma.near < resultD["Matches"]:
                    continue
                if ma.score < max([resultD["Score"], cutoff]):
                    continue
                resultD = {"ID": dbArtistID, "Matches": ma.near, "Score": ma.score, "Best": ma}
                print("\t\t{0: <45}{1}\t{2}\t{3}\t{4} <-- Match".format(dbArtistID, len(artistAlbums), ma.near, ma.score, ma.maxval))

                
        if resultD["ID"] is not None:
            print("\t\t{0: <45}{1}\t{2} <====================================== Best Match".format(resultD["ID"], resultD["Matches"], resultD["Score"]))
            retval[db] = {'ID': resultD["ID"], 'Name': None}
            if "Full" in debug:
                print("\t\t =====>",retval[db])
        else:
            if "Full" in debug:
                print("\t\t =====> No Match")
            retval[db] = None
            
    return retval
            
            
def searchForMutualDBEntries(mdb, num=2, cutoff=0.8, debug=[None], minI=-1, maxR=50):
    retval = {}
    nR = 0
    
    musicArtists = mdb.getArtists()
    for i, artistName in enumerate(musicArtists):
        if i <= minI:
            continue
        result = searchForMutualArtistDBEntries(mdb, artistName, num, cutoff, debug)
        for db,dbval in result.items():
            if dbval is not None:
                if retval.get(artistName) is None:
                    retval[artistName] = {}
                retval[artistName][db] = dbval
                nR += 1
                
        if nR > maxR:
            break
                
    print("Found {0} new artist matches after looping over {1} artists".format(len(retval), i))
    return retval