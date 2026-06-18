#!/bin/bash

#echo "    linting file $1"
./lintsc.py -in "$1" -out "$1"
if [[ $? -ne 0 ]]; then
	exit 1
fi
exit 0
