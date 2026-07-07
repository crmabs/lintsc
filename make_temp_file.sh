#!/bin/bash

function make_tmpfile(){
    
    if [[ -z "$1" ]]; then
        echo 'specify a file prefix! like "sometmp"'
        return 1
    fi
    
    local mydir
    mydir=$(mktemp -d "${TMPDIR:-/tmp/}$(basename $1 ).XXXXXXXXXXXX") &>/dev/null
    local tfil
    tfil=$( mktemp -p "${mydir}"  -t "$(basename $1 ).XXXXXXXXXXXX" ) &>/dev/null
    
    echo "${tfil}"
    
    return 0
}

make_tmpfile "$1"
