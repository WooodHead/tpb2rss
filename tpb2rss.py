#!/bin/env python3

# Imports
from datetime import datetime, timedelta
from html import parser
from re import compile, I, match, search, sub
from sys import argv, exc_info, stderr
from urllib import error, parse, request

# Project info
__author__  = "Ian Brunelli"
__email__   = "ian@brunelli.me"
__version__ = "2.0"
__docs__    = "https://github.com/camporez/tpb2rss/"
__license__ = "Apache License 2.0"

# Don't change these lines
__tpburl__  = "https://thepiratebay.se"
__agent__   = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"

class PageParser(parser.HTMLParser):
	def __init__(self, html):
		parser.HTMLParser.__init__(self)
		self.in_td = False
		self.data = []
		self.feed(html)

	def handle_starttag(self, tag, attrs):
		if tag == "td" and not self.in_td:
			self.in_td = True
			self.data.append("<" + tag)
			for attr in attrs:
				self.data[-1] += " " + attr[0] + "=\"" + attr[1] + "\""
			self.data[-1] += ">"
		elif self.in_td:
			self.data[-1] += "<" + tag
			for attr in attrs:
				self.data[-1] += " " + attr[0] + "=\"" + attr[1] + "\""
			self.data[-1] += ">"

	def handle_data(self, data):
		if self.in_td:
			self.data[-1] += data

	def handle_endtag(self, tag):
		if tag == "td":
			self.data[-1] += "</" + tag + ">"
			self.in_td = False
		elif self.in_td:
			self.data[-1] += "</" + tag + ">"

	def handle_charref(self, ref):
		self.handle_entityref("#" + ref)

	def handle_entityref(self, ref):
		if ref == "nbsp":
			char = " "
		elif ref in ["quote", "amp", "apos", "lt", "gt"]:
			char = "&%s;" % ref
		else:
			char = self.unescape("&%s;" % ref)
		self.handle_data(char)

class Pirate(object):
	def __init__(self, input_string):
		self.get_feed(input_string)

	def get_feed(self, input_string, force_most_recent=True, tpburl=__tpburl__, agent=__agent__):
		try:
			tpburl = search(r"^http(s)?://[\w|\.]+\.[\w|\.]+(:[0-9]+)?/", input_string).group(0)[:-1]
		except:
			pass
		search_string = sub(r">|<|#|&", "", sub(r"^(http(s)?://)?(www.)?" + sub(r"^http(s)?://", "", sub(r".[a-z]*(:[0-9]*)?$", "", tpburl)) + r".[a-z]*(:[0-9]*)?", "", input_string, flags=I))
		info = self.parse_url(search_string.strip(), force_most_recent, tpburl)
		if info:
			link = tpburl + "/" + info[0] + "/" + parse.quote(info[1]) + info[-1]
			page = self.get_page(link, agent)
			try:
				soup = page.read().decode("UTF-8")
			except:
				soup = None
			if soup:
				self.xml = self.xml_constructor(soup, link, tpburl, info)
			else:
				self.xml = None
		else:
			raise ValueError("The given URL is invalid: " + input_string)

	def parse_url(self, search_string, force_most_recent, tpburl):
		url = list(filter(None, search_string.split("/")))
		if (( url[0] == "search" ) or ( url[0] == "user" ) or ( url[0] == "browse" )) and ( len(url) > 1 ):
			if url[-1].isdigit() and url[-2].isdigit() and not url[-3].isdigit():
				url.append("0")
			try:
				if url[-2].isdigit() and url[-3].isdigit() and match(r"^[0-9]+(,[0-9])*$", url[-1]):
					filters = url[-1]
					link = " ".join(url[1:-3])
				else:
					filters = "0"
					link = " ".join(url[1:])
			except:
				filters = "0"
			if not force_most_recent:
				try:
					pag = int(url[-3])
					order = int(url[-2])
				except:
					force_most_recent = True
					filters = "0"
					link = " ".join(url[1:])
			if force_most_recent:
				pag = 0
				order = 3
			return [url[0], link, "/" + str(pag) + "/" + str(order) + "/" + filters + "/"]
		elif url[0] == "recent":
			return [url[0], "", ""]
		elif ( len(url) >= 1 ) and ( not match(r"^http(s)?://", search_string, flags=I) ) and ( not search_string.startswith("/") ):
			search_string = search_string.replace("/", " ")
			return ["search", search_string, "/0/3/0/"]
		return None

	def get_page(self, link, agent):
		try:
			req = request.Request(link, headers={'User-Agent': __agent__})
			page = request.urlopen(req)
			self.status = "200 OK"
			return page
		except error.HTTPError:
			self.status = str(exc_info()[1].code) + " " + exc_info()[1].reason
			return None

	def datetime_parser(self, raw_datetime):
		if "min" in raw_datetime:
			raw_datetime = (datetime.utcnow() - timedelta(minutes=int(sub("[^0-9]", "", raw_datetime)))).strftime("%a, %d %b %Y %H:%M")
			return raw_datetime + ":00"
		elif "Today" in raw_datetime:
			raw_datetime = str(raw_datetime).replace("Today", datetime.utcnow().strftime("%a, %d %b %Y"))
			raw_datetime = (datetime.strptime(raw_datetime, "%a, %d %b %Y %H:%M") - timedelta(hours=2)).strftime("%a, %d %b %Y %H:%M")
			return raw_datetime + ":00"
		elif "Y-day" in raw_datetime:
			raw_datetime = str(raw_datetime).replace("Y-day", (datetime.utcnow() - timedelta(days=1)).strftime("%a, %d %b %Y"))
			raw_datetime = (datetime.strptime(raw_datetime, "%a, %d %b %Y %H:%M") - timedelta(hours=2)).strftime("%a, %d %b %Y %H:%M")
			return raw_datetime + ":00"
		elif ":" in raw_datetime:
			months={"01":"Jan", "02":"Feb", "03":"Mar", "04":"Apr", "05":"May", "06":"Jun", "07":"Jul", "08":"Aug", "09":"Sep", "10":"Oct", "11":"Nov", "12":"Dec"}
			raw_datetime = raw_datetime.split(" ")
			raw_datetime = raw_datetime[0].split("-")[1] + " " + months[raw_datetime[0].split("-")[0]] + " " + datetime.utcnow().strftime("%Y") + " " + str(raw_datetime[1])
			raw_datetime = (datetime.strptime(raw_datetime, "%d %b %Y %H:%M") - timedelta(hours=2)).strftime("%a, %d %b %Y %H:%M")
			return raw_datetime + ":00"
		else:
			weekdays=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
			months={"01":"Jan", "02":"Feb", "03":"Mar", "04":"Apr", "05":"May", "06":"Jun", "07":"Jul", "08":"Aug", "09":"Sep", "10":"Oct", "11":"Nov", "12":"Dec"}
			raw_datetime = raw_datetime.split(" ")
			weekday = datetime.date(datetime.strptime(raw_datetime[1] + "-" + raw_datetime[0].split("-")[0] + "-" + raw_datetime[0].split("-")[1] , "%Y-%m-%d")).weekday()
			raw_datetime = raw_datetime[0].split("-")[1] + " " + months[raw_datetime[0].split("-")[0]] + " " + str(raw_datetime[1])
			return weekdays[weekday] + ", " + raw_datetime + " 00:00:00"

	def find_string(self, raw_list, word):
		for i, s in enumerate(raw_list):
			if word in s:
				position = i
		try:
			return position
		except:
			return None

	def item_constructor(self, item, seeders, leechers, category, tpburl):
		link = "/".join(((item[3]).split("/"))[:3])
		info_hash = (item[9].split(":")[3]).split("&")[0]
		item_xml = "\n\t\t<item>\n\t\t\t"
		title = item[8].split("</a>")[0][1:]
		item_xml += "<title>" + title + "</title>"
		item_xml += "\n\t\t\t<link><![CDATA[" + item[9] + "]]></link>"
		uploaded = item[self.find_string(item, "Uploaded")]
		item_xml += "\n\t\t\t<pubDate>" + self.datetime_parser(" ".join(uploaded.split(",")[0].split(" ")[1:])) + " GMT</pubDate>"
		item_xml += "\n\t\t\t<description><![CDATA["
		item_xml += "Link: " + tpburl + link + "/"
		try:
			item_xml += "<br>Torrent: " + sub(r"^//", "https://", str(item[self.find_string(item, "piratebaytorrents")]))
		except:
			pass
		try:
			item_xml += "<br>Uploader: " + str(item[self.find_string(item, "Browse ")]).replace("Browse ", "")
		except:
			pass
		item_xml += "<br>Category: " + category
		item_xml += "<br>Size: " + " ".join(uploaded.split(",")[1].split(" ")[2:])
		item_xml += "<br>Seeders: " + seeders
		item_xml += "<br>Leechers: " + leechers
		item_xml += "]]></description>"
		item_xml += "\n\t\t\t<guid>" + tpburl + link + "/</guid>"
		item_xml += "\n\t\t\t<torrent xmlns=\"http://xmlns.ezrss.it/0.1/\">"
		item_xml += "\n\t\t\t\t<infoHash>" + info_hash + "</infoHash>"
		item_xml += "\n\t\t\t\t<magnetURI><![CDATA[" + item[9] + "]]></magnetURI>"
		item_xml += "\n\t\t\t</torrent>"
		item_xml += "\n\t\t</item>"
		return item_xml

	def xml_constructor(self, soup, link, tpburl, info):
		page_type = info[0]
		if page_type == "search":
			title = info[1]
		elif page_type in ["browse", "user"]:
			try:
				title = parser.HTMLParser().unescape(search('<title>(.*) - TPB</title>', soup).group(1))
			except:
				title = info[1]
		elif ( page_type == "recent" ):
			title = "Recent Torrents"
		xml = "<rss version=\"2.0\">\n\t" + "<channel>\n\t\t"
		xml += "<title>TPB2RSS: " + title + "</title>\n\t\t"
		xml += "<link>" + link + "</link>\n\t\t"
		xml += "<description>The Pirate Bay " + page_type + " feed for \"" + title + "\"</description>\n\t\t"
		xml += "<lastBuildDate>" + str(datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S")) + " GMT</lastBuildDate>\n\t\t"
		xml += "<language>en-us</language>\n\t\t"
		xml += "<generator>TPB2RSS " + __version__ + "</generator>\n\t\t"
		xml += "<docs>" + __docs__ + "</docs>\n\t\t"
		xml += "<webMaster>" + __email__ + " (" + __author__ + ")</webMaster>"
		tables = PageParser(soup)
		position = 0
		for i in range(int(len(tables.data) / 4)):
			item = str(tables.data[position + 1]).split("\"")
			seeders = str(str(tables.data[position + 2]).split(">")[1]).split("<")[0]
			leechers = str(str(tables.data[position + 3]).split(">")[1]).split("<")[0]
			category = sub(r"(\n|\t)", "", (compile(r'<.*?>').sub('', tables.data[0]).replace("(", " (")))
			xml += self.item_constructor(item, seeders, leechers, category, tpburl)
			position += 4
		xml += "\n\t</channel>" + "\n</rss>"
		return xml

if __name__ == "__main__" and len(argv) > 1:
	result = Pirate(" ".join(argv[1:]))
	if result.xml:
		print(result.xml)
	elif result.status:
		stderr.write(result.status)
