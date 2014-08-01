#!/bin/bash
# This file is a part of TPB2RSS (https://github.com/camporez/tpb2rss/)

FILE="$OPENSHIFT_DATA_DIR/searches"
DIR="$OPENSHIFT_DATA_DIR/raw"
OUTPUTDIR="$OPENSHIFT_DATA_DIR/static"

removefiles() {
	test -f "$1" && rm -f "$1"
}

for INPUT in $DIR/* $OUTPUTDIR/*; do
	ITEM=$( basename "`sed -e 's/\[/\\\[/g' -e 's/\!/\\\!/g' <<< "$INPUT"`" | sed -e 's/\(\.xml\)*$//g' )
	if [ "$ITEM" ]; then
		grep -e ^"$ITEM$" "$FILE" || removefiles "$INPUT"
	fi
done
