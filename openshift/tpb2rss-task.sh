#!/bin/bash

FILE="$OPENSHIFT_DATA_DIR/searches"
DIR="$OPENSHIFT_DATA_DIR/raw"
OUTPUTDIR="$OPENSHIFT_DATA_DIR/static"

for n in $( seq `wc -l <  "$FILE"` ); do
	ITEM=$( head -n$n "$FILE" | tail -n1 )
	if [ $ITEM ]; then
		TMP="$RANDOM"
		FILENAME=$( sed 's/%20/ /g' <<< "$ITEM" )
		wget --quiet -O "$DIR/$TMP" "https://thepiratebay.se/search/$ITEM/0/3/0"
		sed -i -e 's/<a href="[a-z,A-Z,0-9,:,.,\/]*" title="Proxy" target="_blank">Proxy<\/a> \|//g' "$DIR/$TMP"
		sed -i -e "$( expr `grep -i -n footer -m 1 "$DIR/$TMP" | cut -f1 -d":"` - 1 ),$( expr `wc -l < "$DIR/$TMP"` - 1 )d" "$DIR/$TMP"
		if [ $( test -f "$DIR/$FILENAME" && echo 1 ) ]; then
			if [ "$( cat "$DIR/$TMP" )" != "$( cat "$DIR/$FILENAME" )" ]; then
				echo "$FILENAME updated"
				mv "$DIR/$TMP" "$DIR/$FILENAME"
				"$OPENSHIFT_DATA_DIR/tpb2rss.py" "$DIR/$FILENAME" "$OUTPUTDIR/$FILENAME.xml"
			else
				echo "No updates for $FILENAME"; rm "$DIR/$TMP"
			fi
		else
			echo "$FILENAME created"
			mv "$DIR/$TMP" "$DIR/$FILENAME"
			"$OPENSHIFT_DATA_DIR/tpb2rss.py" "$DIR/$FILENAME" "$OUTPUTDIR/$FILENAME.xml"
		fi
	fi
done