from musicdb.albumoftheyear import MediaUtilsdef test_mediautils():    mutils = MediaUtils()    assert hasattr(mutils, 'getMediaID'), f"mutils [{mutils}] does not have getMediaID function"    assert hasattr(mutils, 'compareMedia'), f"mutils [{mutils}] does not have compareMedia function"