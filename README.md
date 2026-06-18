This is a simple standalone script to format SuperCollider Sclang files mainly *.sc and *.scd.
Coded by some ml coding agent given the following instructions:


Name: LintSc

Description: Supercollider sclang linter utility that formats sclang source files written in Python

Input: single source file  *.sc *.scd
Output: the formatted file with "f_" file name prefix if no -out command line argument is defined

Rules of formatting:
- Keep maximum of 2 consequent empty lines outside of functions
- Keep maximum of 1 empty line with a function
- Don't format line comments just indent them. These are lines marked with //
- Don't format block comments and don't indent them. These are blocks of text between  /* and */
- Indent the source file according to sclang traditions. Very similar to javascript or c#. Make it compact and easy to read
- Operate only on empty spaces, spaces, newlines, tab characters. The source must be kept intact otherwise. 
- Verify opening and closing of brackets. They must be present as pairs always. The bracket pairs are: {} [] ()
- Verify occurrences of unpaired closing brackets. These are: } ] )
- When a bracketing mismatch is found print out the error message that will help me to find it in the source then exit with an error code


Coding instructions:
- the program will be run in a bash shell on linux Ubuntu 
- use Python for the language
- make it a command line utility with arguments: -in inputfile with an optional -out output file. otherwise add "f_" prefix to the filename and save like that
