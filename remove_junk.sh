#!/bin/bash

proot="$1"
if [[ -z "${proot}" ]]; then
	proot="."
fi

echo "remove format junk. files like f_*.sc f_*.scd"
find "${proot}" -type f \( -name "f_*.sc" -o -name "f_*.scd" \) -exec rm -fv "{}" \;

