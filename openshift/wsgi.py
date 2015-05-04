# This file is a part of TPB2RSS (https://github.com/camporez/tpb2rss/)

import os
import sys
from tpb2rss import Pirate
from page import build

def feed_generator(path_info):
	global error
	try:
		result = Pirate(path_info)
		return result
	except:
		error = str(sys.exc_info()[1])
		return None

def application(environ, start_response):
	global error
	status = "200 OK"
	error = ""

	if (( environ["PATH_INFO"] == "") or ( environ["PATH_INFO"] == "/" )):
		xml = False
	else:
		result = feed_generator(environ["PATH_INFO"].encode("iso-8859-1").decode("utf-8"))
		try:
			status = result.status
			xml = result.xml
		except:
			status = "404 Not Found"
			xml = None
	if xml:
		ctype = "text/xml; charset=UTF-8"
		response_body = xml
	else:
		ctype = "text/html; charset=UTF-8"
		response_body = build(xml, error, status)

	response_headers = [("Content-Type", ctype), ("Content-Length", str(len(response_body.encode("UTF-8"))))]

	start_response(status, response_headers)
	return [response_body.encode("UTF-8")]
