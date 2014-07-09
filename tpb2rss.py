#!/bin/env python2
# -*- coding: cp1252 -*-
from bs4 import BeautifulSoup
import sys
import datetime
import urllib2

def open_url(search_string):
	global soup
	url = "https://thepiratebay.se/search/" + search_string + "/0/3/0"
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())

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
		exit()

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

def item_constructor(item, seeders, leechers):
	item_xml = "\n\t\t\t<item>\n\t\t\t\t<title>" + str(item[8]).split("</a>")[0][1:] + "</title>"
	item_xml += "\n\t\t\t\t<link><![CDATA[ " + item[9] + " ]]></link>"
	uploaded = item[find_string(item, "Uploaded")]
	item_xml += "\n\t\t\t\t<pubDate>" + datetime_parser(uploaded.split(" ")[1][:-1]) + " GMT</pubDate>"
	item_xml += "\n\t\t\t\t<description>Link: https://thepiratebay.org" + str(item[5])
	if find_string(item, "piratebaytorrents"):
		item_xml += "\nTorrent: " + str(item[find_string(item, "piratebaytorrents")]).replace("//piratebaytorrents", "https://piratebaytorrents")
	if find_string(item, "Browse "):
		item_xml += "\nUploader: " + str(item[find_string(item, "Browse ")]).replace("Browse ", "")
	item_xml += "\nSize: " + uploaded.split(" ")[3][:-1]
	item_xml += "\nSeeders: " + seeders
	item_xml += "\nLeechers: " + leechers + "</description>\n\t\t\t</item>"
	return item_xml

def main_program(soup):
	title = str(soup.span.contents[0]).split(": ")[1]
	xml = "<rss version=\"2.0\">\n\t<channel>\n\t\t<title>TPB2RSS: " + title + "</title>\n" + "\t\t<link>http://thepiratebay.org/search/" + title.replace(" ", "%20") + "/0/3/0</link>\n\t\t<description>The Pirate Bay search feed for \"" + title + "\"</description>\n" + "\t\t<lastBuildDate>" + str(datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S")) + " GMT</lastBuildDate>\n\t\t<language>en-us</language>\n\t\t<generator>TPB2RSS 1.0</generator>\n\t\t<docs>http://github.com/camporez/tpb2rss</docs>\n\t\t<webMaster>ian@camporez.com</webMaster>"
	tables = soup("td")
	position = 0
	for i in range(len(tables) / 4):
		item = str(tables[position + 1]).split("\"")
		seeders = str(str(tables[position + 2]).split(">")[1]).split("<")[0]
		leechers = str(str(tables[position + 3]).split(">")[1]).split("<")[0]
		xml += item_constructor(item, seeders, leechers)
		position += 4
	xml += "\n\t</channel>" + "\n</rss>"
	return xml

if (len(sys.argv) == 2) or (len(sys.argv) == 3):
	try:
		open_file(sys.argv[1])
	except:
		open_url(sys.argv[1])
	xml = main_program(soup)
	if len(sys.argv) >= 3:
		write_file(sys.argv[2], xml)
	else:
		print xml
else:
	print "Usage:", sys.argv[0], "( INPUT_FILE | SEARCH_TERM ) [ OUTPUT_FILE ]"
