#!/bin/bash

proot="$1"
if [[ -z "${proot}" ]]; then
	proot="."
fi

echo "delete backup"
find "${proot}" -type f \( -name "*.sc.bak" -o -name "*.scd.bak" \) -exec rm -fv "{}" \;

