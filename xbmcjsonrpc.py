import jsonrpclib

server = jsonrpclib.Server('http://localhost:8080/jsonrpc')

def safeGet(d, k, v):
	if d == None:
		return v

	vv = d.get(k, v)
	if vv == None:
		return v
	else:
		return vv

def getSources():
	result = server.Files.GetSources(media="video")
	return safeGet(result, "sources", [])

def getDirectory(directory):
	result = server.Files.GetDirectory(directory)
	return safeGet(result, "files", [])

def getMovies(properties):
	result = server.VideoLibrary.GetMovies(properties=properties)
	return safeGet(result, "movies", [])

def getEpisodes(properties):
	result = server.VideoLibrary.GetEpisodes(properties=properties)
	return safeGet(result, "episodes", [])

def getTVShows(properties):
	result = server.VideoLibrary.GetTVShows(properties=properties)
	return safeGet(result, "tvshows", [])
