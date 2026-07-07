#!/bin/bash

# all files from here
# find . -type f \( -name "*.sc" -o -name "*.scd" \) -exec ./lintonefile.sh "{}" \;

proot="$1"
if [[ -z "${proot}" ]]; then
	proot="."
fi

proot=$( realpath "${proot}" )
echo "linting dir: ${proot}" 

tmpf=$( ./make_temp_file.sh linttmp   )

remove_junk(){
	rm -rfv "${tmpf}"
}

trap remove_junk EXIT


while IFS= read -r line; do
    # Process "$line" here
    ./lintsc.py -in "$line" -out "${tmpf}"
    if [[ $? -ne 0 ]]; then
		echo "PROBLEM with file: ${line}"
		echo ""		
		exit 1
    fi
done < <( find "${proot}" -type f \( -name "*.sc" -o -name "*.scd" \)  )

echo "All files processed."
echo ""
exit 0
