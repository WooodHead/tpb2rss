# This file is a part of TPB2RSS (https://github.com/camporez/tpb2rss/)

from page    import build
from sys     import exc_info
from tpb2rss import ThePirateFeed

def feed_generator(path_info):
	global error
	try:
		result = ThePirateFeed(path_info)
		return result
	except:
		error = str(exc_info()[1])
		return None

def application(environ, start_response):
	global error
	status = "200 OK"
	error = ""

	if (( environ["PATH_INFO"] == "") or ( environ["PATH_INFO"] == "/" )):
		xml = False
	else:
		result = feed_generator(environ["PATH_INFO"].encode("ISO-8859-1").decode("UTF-8"))
		try:
			status = "%i %s" % (result.status.code, result.status.reason)
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
