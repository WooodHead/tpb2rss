#!/bin/env python2
# -*- coding: cp1252 -*-
from bs4 import BeautifulSoup
import sys
import datetime
import urllib2

def url_parser(search_string, preserve_pag_order):
	url = filter(None, search_string.split("/"))
	if (( url[0] == "http:" ) or ( url[0] == "https:" )) and ( url[1].startswith("thepiratebay") and ( len(url) >= 4 ) ):
		try:
			filters = url[6]
		except:
			filters = "0"
		if preserve_pag_order:
			try:
				pag = int(url[4])
				order = int(url[5])
			except:
				preserve_pag_order = False
				filters = "0"
		if not preserve_pag_order:
			pag = "0"
			order = "3"
		return [url[2], url[3].decode('iso-8859-1').encode('utf8'), str(pag), str(order), filters]
	elif (( url[0] == "search" ) or ( url[0] == "user" ) or ( url[0] == "browse" )) and ( len(url) > 1 ):
		try:
			filters = url[4]
		except:
			filters = "0"
		if preserve_pag_order:
			try:
				pag = int(url[2])
				order = int(url[3])
			except:
				preserve_pag_order = False
				filters = "0"
		if not preserve_pag_order:
			pag = "0"
			order = "3"
		return [url[0], url[1].decode('iso-8859-1').encode('utf8'), str(pag), str(order), filters]
	elif ( len(url) == 1 ) and ( not search_string.startswith("/") ):
		return ["search", search_string.decode('iso-8859-1').encode('utf8'), "0", "3" "0"]
	return None

def open_url(search_string, preserve_pag_order):
	global soup, info, link
	info = url_parser(search_string, preserve_pag_order)
	if info:
		link = "http://thepiratebay.se/" + info[0] + "/" + info[1].decode('utf8').encode('iso-8859-1') +  "/" + "/".join(info[2:5])
		try:
			page = urllib2.urlopen(link)
		except:
			print "Couldn't open the URL"
			exit(1)
		soup = BeautifulSoup(page.read())
	else:
		print "The given string is invalid:", search_string
		exit(1)

def open_file(input_file):
	global soup
	file = open(input_file)
	soup = BeautifulSoup(file.read())
	file.close()

def write_file(output_file, content):
	try:
		file = open(output_file, "w")
		file.write(content)
		file.close()
	except:
		print "Couldn't write file:", output_file
		exit(1)

def datetime_parser(raw_datetime):
	if "mins" in raw_datetime:
		raw_datetime = str(raw_datetime).replace(" mins ago", "")
		raw_datetime = str(raw_datetime).replace("<b>", "")
		raw_datetime = str(raw_datetime).replace("</b>", "")
		raw_datetime = (datetime.datetime.utcnow() - datetime.timedelta(minutes=int(raw_datetime))).strftime("%a, %d %b %Y %H:%M")
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

def item_constructor(item, seeders, leechers, category):
	link = "/".join(((item[5]).split("/"))[:3])
	info_hash = (item[9].split(":")[3]).split("&")[0]
	item_xml = "\n\t\t<item>\n\t\t\t<title>" + str(item[8]).split("</a>")[0][1:] + "</title>"
	item_xml += "\n\t\t\t<link><![CDATA[" + item[9] + "]]></link>"
	uploaded = item[find_string(item, "Uploaded")]
	item_xml += "\n\t\t\t<pubDate>" + datetime_parser(uploaded.split(" ")[1][:-1]) + " GMT</pubDate>"
	item_xml += "\n\t\t\t<description><![CDATA[Link: https://thepiratebay.se" + link + "/"
	if find_string(item, "piratebaytorrents"):
		item_xml += "<br>Torrent: " + str(item[find_string(item, "piratebaytorrents")]).replace("//piratebaytorrents", "https://piratebaytorrents")
	if find_string(item, "Browse "):
		item_xml += "<br>Uploader: " + str(item[find_string(item, "Browse ")]).replace("Browse ", "")
	item_xml += "<br>Category: " + category
	item_xml += "<br>Size: " + uploaded.split(" ")[3][:-1]
	item_xml += "<br>Seeders: " + seeders
	item_xml += "<br>Leechers: " + leechers + "]]></description>"
	item_xml += "\n\t\t\t<guid>https://thepiratebay.se" + link + "/</guid>"
	item_xml += "\n\t\t\t<torrent xmlns=\"http://xmlns.ezrss.it/0.1/\">"
	item_xml += "\n\t\t\t\t<infoHash>" + info_hash + "</infoHash>"
	item_xml += "\n\t\t\t\t<magnetURI><![CDATA[" + item[9] + "]]></magnetURI>"
	item_xml += "\n\t\t\t</torrent>\n\t\t</item>"
	return item_xml

def xml_constructor(soup):
	page_type = info[0]
	if page_type == "search":
		title = info[1].replace("%20", " ")
	elif ( page_type == "browse" ):
		title = str(" ".join((soup.span.contents[0].split(" "))[1:]))
	elif ( page_type == "user" ):
		title = info[1]
	title = title.decode('utf8').encode('iso-8859-1')
	xml = "<rss version=\"2.0\">\n\t<channel>\n\t\t<title>TPB2RSS: " + title + "</title>\n" + "\t\t<link>" + link + "/</link>\n\t\t<description>The Pirate Bay " + page_type + " feed for \"" + title + "\"</description>\n" + "\t\t<lastBuildDate>" + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S")) + " GMT</lastBuildDate>\n\t\t<language>en-us</language>\n\t\t<generator>TPB2RSS 1.0</generator>\n\t\t<docs>http://github.com/camporez/tpb2rss/</docs>\n\t\t<webMaster>ian@camporez.com</webMaster>"
	tables = soup("td")
	position = 0
	for i in range(len(tables) / 4):
		item = str(tables[position + 1]).split("\"")
		seeders = str(str(tables[position + 2]).split(">")[1]).split("<")[0]
		leechers = str(str(tables[position + 3]).split(">")[1]).split("<")[0]
		category = ((''.join( BeautifulSoup(str(tables[position])).findAll( text = True ) )).replace("\t", "")).replace("\n", " ")[2:].decode('iso-8859-1').encode('utf8')
		xml += item_constructor(item, seeders, leechers, category)
		position += 4
	xml += "\n\t</channel>" + "\n</rss>"
	return xml

def xml_from_url(search_string):
	open_url(search_string, False)
	xml = xml_constructor(soup)
	return xml

if (len(sys.argv) == 2) or (len(sys.argv) == 3):
	try:
		open_file(sys.argv[1])
	except:
		open_url(sys.argv[1], False)
	xml = xml_constructor(soup)
	if len(sys.argv) >= 3:
		write_file(sys.argv[2], xml)
	else:
		print xml
