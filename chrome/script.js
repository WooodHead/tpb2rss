if (/^((http)s{0,1}:\/\/(www.){0,1}){0,1}thepiratebay\.[a-z]+\/(search\/(.)+|browse\/[0-9]+|recent)+/.test(location.href)) {
	if (/^((http)s{0,1}:\/\/(www.){0,1}){0,1}thepiratebay\.[a-z]+\/browse\/[0-9]+/.test(location.href)) {
		var url = "http://rss.thepiratebay.se/" + window.location.pathname.split("/")[2]
	} else {
		var url = document.URL;
		var url = url.replace(/^((http)s{0,1}:\/\/(www.){0,1}){0,1}thepiratebay\.[a-z]{1,}\//gi, "http://bay.brunelli.me/");
	}
	var content = document.getElementsByTagName("h2")[0].innerHTML;
	document.getElementsByTagName("h2")[0].innerHTML = content + "&nbsp;<a class=\"rss\" href=\"" + url + "\" title=\"Subscribe to this page\"><img src=\"/static/img/rss_small.gif\" alt=\"RSS\" border=\"0\" /></a>";
}
