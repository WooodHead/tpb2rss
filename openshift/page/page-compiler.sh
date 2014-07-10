#!/bin/bash

pythonize() {
	sed -i 's/"/\\"/g' "$1"
	sed -i 's/\t/\\t/g' "$1"
	sed -i ':a;N;$!ba;s/\n/"\nhtml += "/g' "$1"
	sed -i '1s/^/html = \"/' "$1"
	sed -i '$s/$/\"/' "$1"
	sed -i ':a;N;$!ba;s/\"\nhtml += \"\"\n/\\n"\n/g' "$1"
}

cp tpb2rss.html tpb2rss.py && pythonize tpb2rss.py
