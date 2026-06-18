



# multiple patterns
find . -type f \( -name "*.sc" -o -name "*.scd" \) -exec ./lintonefile.sh "{}" \;

# Define your function
generate_data() {
    echo "Line 1"
    echo "Line 2"
    echo "Line 3"
}

# Process the function output line-by-line
while IFS= read -r line; do
    echo "Processing: $line"
done < <(generate_data)   

The < <(function_name) construct creates a temporary FIFO (named pipe) that read consumes. 
his avoids the subshell issue caused by piping (|), ensuring variables modified inside the loop persist afterwards.

----------------------------------------------------------

Loading Function Output into an Array
If you need random access to the lines or are using Bash 4+, use mapfile (also known as readarray) with process substitution. 

# Load function output directly into an array
mapfile -t lines < <(generate_data)

# Iterate over the array
for line in "${lines[@]}"; do
    echo "Array item: $line"
done

Note: The -t flag removes trailing newlines from each element. 
This method loads the entire output into memory, so it is best for moderate-sized data sets
