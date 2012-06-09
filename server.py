import urllib2
import json

server_base_address = "http://127.0.0.1:8000"

def post(address, d):
	h = {
		"Content-Type": "application/json",

		# Some extra headers for fun
		"Accept": "*/*",   # curl does this
		"User-Agent": "xbmc-gsoc2012-statistics", # otherwise it uses "Python-urllib/..."
	}

	req = urllib2.Request(address, headers = h, data = d)

	f = urllib2.urlopen(req)

def uploadMedia(media, data):
	post(server_base_address + "/" + media, json.dumps(data))
