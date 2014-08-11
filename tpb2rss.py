#!/bin/env python2

# Imports
from bs4 import BeautifulSoup
import sys
import re
import datetime
import urllib2

# Project info
__author__  = "Ian Camporez Brunelli"
__email__   = "ian@camporez.com"
__version__ = "1.1"
__docs__    = "https://github.com/camporez/tpb2rss/"
__license__ = "Apache License 2.0"

# Changing this URL isn't the right way to use a mirror
__tpburl__  = "https://thepiratebay.se"

def url_parser(search_string, keep_pagination_order, tpburl):
	url = filter(None, search_string.split("/"))
	if (( url[0] == "search" ) or ( url[0] == "user" ) or ( url[0] == "browse" )) and ( len(url) > 1 ):
		if url[-1].isdigit() and url[-2].isdigit() and not url[-3].isdigit():
			url.append("0")
		try:
			if url[-2].isdigit() and url[-3].isdigit() and re.match(r"^[0-9]+(,[0-9])*$", url[-1]):
				filters = url[-1]
				link = " ".join(url[1:-3])
			else:
				filters = "0"
				link = " ".join(url[1:])
		except:
			filters = "0"
		if keep_pagination_order:
			try:
				pag = int(url[-3])
				order = int(url[-2])
			except:
				keep_pagination_order = False
				filters = "0"
				link = " ".join(url[1:])
		if not keep_pagination_order:
			pag = 0
			order = 3
		return [url[0], link.decode("iso-8859-1").encode("utf8"), "/" + str(pag) + "/" + str(order) + "/" + filters + "/"]
	elif url[0] == "recent":
		return [url[0], ""]
	elif ( len(url) >= 1 ) and ( not re.match(r"^http(s)?://", search_string, flags=re.I) ) and ( not search_string.startswith("/") ):
		search_string = search_string.replace("/", " ")
		return ["search", search_string.decode("iso-8859-1").encode("utf8"), "/0/3/0/"]
	return None

def open_url(search_string, keep_pagination_order, tpburl):
	global soup, info, link
	search_string = re.sub(r">|<|#|&", "", re.sub(r"^(http(s)?://)?(www.)?" + re.sub(r"^http(s)?://", "", re.sub(r".[a-z]*(:[0-9]*)?$", "", tpburl)) + r".[a-z]*(:[0-9]*)?", "", search_string, flags=re.I))
	info = url_parser(search_string.strip(), keep_pagination_order, tpburl)
	if info:
		link = tpburl + "/" + info[0] + "/" + info[1].decode("utf8").encode("iso-8859-1") + info[-1]
		try:
			page = urllib2.urlopen(link)
		except:
			print >> sys.stderr, "Couldn't open the URL"
			exit(1)
		soup = BeautifulSoup(page.read())
	else:
		print >> sys.stderr, "The given URL is invalid:", tpburl + search_string
		exit(1)

def open_file(input_file, keep_pagination_order, tpburl):
	global soup, info, link
	file = open(input_file)
	soup = BeautifulSoup(file.read())
	try:
		link = str((soup.findAll("link", rel="canonical")[0])).split("\"")[1]
		tpburl = re.search(r"^http(s)?://[\w|\.]+\.[\w|\.]+(:[0-9]+)?/", link).group(0)[:-1]
		search_string = re.sub(r">|<|#|&", "", re.sub(r"^(http(s)?://)?(www.)?" + re.sub(r"^http(s)?://", "", re.sub(r".[a-z]*(:[0-9]*)?$", "", tpburl)) + r".[a-z]*", "", link, flags=re.I))
		info = url_parser(search_string.strip(), keep_pagination_order, tpburl)
		link = tpburl + "/" + info[0] + "/" + info[1].decode("utf8").encode("iso-8859-1") + info[-1]
	except:
		print >> sys.stderr, "The given file is invalid:", input_file
		exit(1)
	file.close()

def write_file(output_file, content):
	try:
		file = open(output_file, "w")
		file.write(content)
		file.close()
	except:
		print >> sys.stderr, "Couldn't write file:", output_file
		exit(1)

def datetime_parser(raw_datetime):
	if "min" in raw_datetime:
		raw_datetime = (datetime.datetime.utcnow() - datetime.timedelta(minutes=int(re.sub("[^0-9]", "", raw_datetime)))).strftime("%a, %d %b %Y %H:%M")
		return raw_datetime + ":00"
	elif "Today" in raw_datetime:
		raw_datetime = str(raw_datetime).replace("Today", datetime.datetime.utcnow().strftime("%a, %d %b %Y"))
		return raw_datetime + ":00"
	elif "Y-day" in raw_datetime:
		raw_datetime = str(raw_datetime).replace("Y-day", (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%a, %d %b %Y"))
		return raw_datetime + ":00"
	elif ":" in raw_datetime:
		weekdays=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
		months={"01":"Jan", "02":"Feb", "03":"Mar", "04":"Apr", "05":"May", "06":"Jun", "07":"Jul", "08":"Aug", "09":"Sep", "10":"Oct", "11":"Nov", "12":"Dec"}
		raw_datetime = raw_datetime.split("\xc2\xa0")
		weekday = datetime.date(int(datetime.datetime.utcnow().strftime("%Y")),int(raw_datetime[0].split("-")[0]),int(raw_datetime[0].split("-")[1])).weekday()
		raw_datetime = raw_datetime[0].split("-")[1] + " " + months[raw_datetime[0].split("-")[0]] + " " + datetime.datetime.utcnow().strftime("%Y") + " " + str(raw_datetime[1])
		return weekdays[weekday] + ", " + raw_datetime + ":00"
	else:
		weekdays=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
		months={"01":"Jan", "02":"Feb", "03":"Mar", "04":"Apr", "05":"May", "06":"Jun", "07":"Jul", "08":"Aug", "09":"Sep", "10":"Oct", "11":"Nov", "12":"Dec"}
		raw_datetime = raw_datetime.split("\xc2\xa0")
		weekday = datetime.date(int(raw_datetime[1]),int(raw_datetime[0].split("-")[0]),int(raw_datetime[0].split("-")[1])).weekday()
		raw_datetime = raw_datetime[0].split("-")[1] + " " + months[raw_datetime[0].split("-")[0]] + " " + str(raw_datetime[1])
		return weekdays[weekday] + ", " + raw_datetime + " 00:00:00"

def find_string(raw_list, word):
	for i, s in enumerate(raw_list):
		if word in s:
			position = i
	try:
		return position
	except:
		return None

def item_constructor(item, seeders, leechers, category, tpburl):
	link = "/".join(((item[5]).split("/"))[:3])
	info_hash = (item[9].split(":")[3]).split("&")[0]
	item_xml = "\n\t\t<item>\n\t\t\t<title>" + str(item[8]).split("</a>")[0][1:] + "</title>"
	item_xml += "\n\t\t\t<link><![CDATA[" + item[9] + "]]></link>"
	uploaded = item[find_string(item, "Uploaded")]
	item_xml += "\n\t\t\t<pubDate>" + datetime_parser(uploaded.split(" ")[1][:-1]) + " GMT</pubDate>"
	item_xml += "\n\t\t\t<description><![CDATA[Link: " + tpburl + link + "/"
	if find_string(item, "piratebaytorrents"):
		item_xml += "<br>Torrent: " + re.sub(r"^//", "https://", str(item[find_string(item, "piratebaytorrents")]))
	if find_string(item, "Browse "):
		item_xml += "<br>Uploader: " + str(item[find_string(item, "Browse ")]).replace("Browse ", "")
	item_xml += "<br>Category: " + category
	item_xml += "<br>Size: " + uploaded.split(" ")[3][:-1]
	item_xml += "<br>Seeders: " + seeders
	item_xml += "<br>Leechers: " + leechers + "]]></description>"
	item_xml += "\n\t\t\t<guid>" + tpburl + link + "/</guid>"
	item_xml += "\n\t\t\t<torrent xmlns=\"http://xmlns.ezrss.it/0.1/\">"
	item_xml += "\n\t\t\t\t<infoHash>" + info_hash + "</infoHash>"
	item_xml += "\n\t\t\t\t<magnetURI><![CDATA[" + item[9] + "]]></magnetURI>"
	item_xml += "\n\t\t\t</torrent>\n\t\t</item>"
	return item_xml

def xml_constructor(soup, tpburl):
	page_type = info[0]
	if page_type == "search":
		title = info[1].replace("%20", " ")
	elif ( page_type == "browse" ):
		title = str(" ".join((soup.span.contents[0].split(" "))[1:]))
	elif ( page_type == "user" ):
		title = info[1]
	elif ( page_type == "recent" ):
		title = "Recent Torrents"
	title = title.decode("utf8").encode("iso-8859-1")
	xml = "<rss version=\"2.0\">\n\t<channel>\n\t\t<title>TPB2RSS: " + title + "</title>\n" + "\t\t<link>" + link + "</link>\n\t\t<description>The Pirate Bay " + page_type + " feed for \"" + title + "\"</description>\n" + "\t\t<lastBuildDate>" + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S")) + " GMT</lastBuildDate>\n\t\t<language>en-us</language>\n\t\t<generator>TPB2RSS " + __version__ + "</generator>\n\t\t<docs>" + __docs__ + "</docs>\n\t\t<webMaster>" + __email__ + "</webMaster>"
	tables = soup("td")
	position = 0
	for i in range(len(tables) / 4):
		item = str(tables[position + 1]).split("\"")
		seeders = str(str(tables[position + 2]).split(">")[1]).split("<")[0]
		leechers = str(str(tables[position + 3]).split(">")[1]).split("<")[0]
		category = ((re.sub(r"(\n|\t)", "", ("".join( BeautifulSoup(str(tables[position])).findAll( text = True ) )))).replace("(", " (")).decode("iso-8859-1").encode("utf8")
		xml += item_constructor(item, seeders, leechers, category, tpburl)
		position += 4
	xml += "\n\t</channel>" + "\n</rss>"
	return xml

def xml_from_file(filename, keep_pagination_order=True, tpburl=__tpburl__):
	open_file(filename, keep_pagination_order, tpburl)
	xml = xml_constructor(soup, tpburl)
	return xml

def xml_from_url(search_string, keep_pagination_order=False, tpburl=__tpburl__):
	try:
		tpburl = re.search(r"^http(s)?://[\w|\.]+\.[\w|\.]+(:[0-9]+)?/", search_string).group(0)[:-1]
	except:
		pass
	open_url(search_string, keep_pagination_order, tpburl)
	xml = xml_constructor(soup, tpburl)
	return xml

def main(parameters):
	if (len(parameters) == 2) or (len(parameters) == 3):
		try:
			xml = xml_from_file(parameters[1])
		except IOError:
			xml = xml_from_url(parameters[1])
		try:
			write_file(parameters[2], xml)
		except IndexError:
			print xml

if __name__ == "__main__":
	main(sys.argv)
