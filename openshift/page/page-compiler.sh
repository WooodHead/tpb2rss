#!/bin/bash
# This file is a part of TPB2RSS (https://github.com/camporez/tpb2rss/)

pythonize() {
	sed -i 's/"/\\"/g' "$1"
	sed -i 's/\t/\\t/g' "$1"
	sed -i ':a;N;$!ba;s/\n/"\n\thtml += "\\n/g' "$1"
	sed -i '1s/^/\thtml = \"/' "$1"
	sed -i '2s/^/\tif error:\n\t\thtml += "\\n<!-- " + error + " -->"\n/' "$1"
	sed -i '$s/$/\"/' "$1"
	sed -i ':a;N;$!ba;s/\"\n\thtml += \"\"\n/\\n"\n/g' "$1"
	sed -i '1i # This file is a part of TPB2RSS (https://github.com/camporez/tpb2rss)\n\n\def build(xml, error, status):' "$1"
	sed -i '$a\\treturn html' "$1"
	for line in "$( grep -in "Page not found" "$1" | cut -f 1 -d ':' )"; do
		nf=$( cat "$1" | head -n $line | tail -n 1 | sed 's/\//\\\//g' | sed 's/\\n/\\\\n/g' | sed 's/\\t/\\\\t/g' | sed 's/\\"/\\\\"/g' )
		sed -i "s/.*not found.*/\tif xml == None:\n\t$nf/g" "$1"
	done
	sed -i 's/Page not found/" + status + "/g' "$1"
}

cp page.html ../page.py && pythonize ../page.py
