#!/bin/bash

FILE="$OPENSHIFT_DATA_DIR/searches"
DIR="$OPENSHIFT_DATA_DIR/raw"

removefiles() {
	test -f "$1" && rm -f "$1"
	test -f "$( dirname "$1" )/../static/$( basename "$1" ).xml" && rm -f "$( dirname "$1" )/../static/$( basename "$1" ).xml"
}

for INPUT in $DIR/*; do
	ITEM=$( basename "`sed -e 's/\[/\\\[/g' -e 's/\!/\\\!/g' <<< "$INPUT"`" )
	if [ "$ITEM" ]; then
		grep -e ^"$ITEM$" "$FILE" || removefiles "$INPUT"
	fi
done
