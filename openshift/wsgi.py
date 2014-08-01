# This file is a part of TPB2RSS (https://github.com/camporez/tpb2rss/)

import os
import datetime
import urllib2
import tpb2rss
import page

def feed_generator(path_info):
	try:
		xml = tpb2rss.xml_from_url(path_info)
		return xml
	except:
		return None

def application(environ, start_response):
	status = "200 OK"

	if (( environ["PATH_INFO"] == "") or ( environ["PATH_INFO"] == "/" )):
		xml = False
	else:
		xml = feed_generator(environ['PATH_INFO'])
	if xml:
		ctype = "text/xml"
		response_body = xml
	else:
		ctype = "text/html"
		if xml == None:
			status = "404 Not Found"
		response_body = page.build(xml)

	response_headers = [("Content-Type", ctype), ("Content-Length", str(len(response_body)))]

	start_response(status, response_headers)
	return [response_body]
