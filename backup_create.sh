#!/bin/bash

proot="$1"
if [[ -z "${proot}" ]]; then
	proot="."
fi

echo "making backup"
find "${proot}" -type f \( -name "*.sc" -o -name "*.scd" \) -exec cp -fv "{}" "{}.bak"  \;

