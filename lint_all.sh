#!/bin/bash

# all files from here
# find . -type f \( -name "*.sc" -o -name "*.scd" \) -exec ./lintonefile.sh "{}" \;

proot="$1"
if [[ -z "${proot}" ]]; then
	proot="."
fi

proot=$( realpath "${proot}" )
echo "linting dir: ${proot}" 






./backup_create.sh "${proot}"
echo " backup done"
#trap remove_junk EXIT


while IFS= read -r line; do
    # Process "$line" here
    ./in_place_lint_one_file.sh "$line"
    if [[ $? -ne 0 ]]; then
		echo "PROBLEM with file: ${line}"
		echo ""
		./backup_restore.sh "${proot}"
		echo " files restored - but you must fix the code"
		exit 1
    fi
done < <( find "${proot}" -type f \( -name "*.sc" -o -name "*.scd" \)  )

echo "All files formatted."
echo ""
if [[ "$2" == "-s" ]]; then
	
	
	echo "running test.   Arg -s was specified"
	
	#timeout -s SIGQUIT 6 sclang -d /home/crm/work/opto /home/crm/work/opto/opto.scd
	timeout -s SIGQUIT 6 sclang -d "$3" "$4"
	if [[ $? -eq 0 ]]; then
		echo "compile failed ->"
		./backup_restore.sh "${proot}"
		exit 1
	else
		echo "OK compiled OK"
		./backup_delete.sh "${proot}"
		exit 0
	fi



else

	echo "skipping execution test.   Specif -s workdir startfile "
	./backup_delete.sh "${proot}"
	echo "Done."
	exit 0

fi
