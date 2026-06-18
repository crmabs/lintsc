#!/bin/bash

proot="$1"
if [[ -z "${proot}" ]]; then
	proot="."
fi

echo "lintable files"
find "${proot}" -type f \( -name "*.sc" -o -name "*.scd" \)

