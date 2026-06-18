#!/bin/bash

proot="$1"
if [[ -z "${proot}" ]]; then
	proot="."
fi

proot=$( realpath "$proot" )

echo ""
echo "restoring backup of folder:[${proot}]"
while IFS= read -r line; do
    # Process "$line" here
	cf=$( basename -s .bak "$line" )
    mv -fv "$line" "$cf"
    
    
done < <( find "${proot}" -type f \( -name "*.sc.bak" -o -name "*.scd.bak" \)  )
