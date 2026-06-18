# LintSc Usage Guide

LintSc is a Supercollider sclang linter utility that formats sclang source files. It's written in Python and provides professional code formatting with bracket validation.

## Installation

No additional dependencies required. Just Python 3.6+.

```bash
chmod +x lintsc.py
```

## Usage

### Basic Usage
Format a file with automatic output naming (adds "f_" prefix):
```bash
python3 lintsc.py -in myfile.sc
```

This creates `f_myfile.sc` with the formatted content.

### Specify Output File
```bash
python3 lintsc.py -in myfile.scd -out formatted.scd
```

### Help
```bash
python3 lintsc.py -h
```

## Features

### Formatting Rules
1. **Empty Lines**: Maintains a maximum of 2 consecutive empty lines (more compact formatting)
2. **Comments Preserved**: 
   - Line comments (`//`) are preserved and properly indented
   - Block comments (`/* ... */`) are preserved exactly as-is
3. **Indentation**: Uses tab characters for indentation, following sclang conventions similar to JavaScript and C#
4. **Bracket Validation**: Verifies all bracket pairs are properly matched:
   - `{}` - Curly braces
   - `[]` - Square brackets
   - `()` - Parentheses

### Error Handling
If bracket mismatches are found, the tool will:
1. Print an error message with the line and column number
2. Indicate which bracket is unmatched and which opening bracket it's trying to match
3. Exit with error code 1

Example error message:
```
Error: Line 3, Column 17: Found ')' but expected ']' (matching '[' from line 3, column 9)
```

## Examples

### Example 1: Simple Formatting
Input file:
```supercollider
(
var x = 100;
var y = [1,2,3];
)
```

Output file:
```supercollider
(
	var x = 100;
	var y = [1,2,3];
)
```

### Example 2: Function with Comments
Input:
```supercollider
{
// This is a comment
var freq = 440;
SinOsc.ar(freq)
}.play;
```

Output:
```supercollider
{
	// This is a comment
	var freq = 440;
	SinOsc.ar(freq)
}.play;
```

### Example 3: Complex Nested Structure
Input:
```supercollider
(
a: 1,
b: (
inner: 2,
nested: [1, 2, 3]
)
)
```

Output:
```supercollider
(
	a: 1,
	b: (
		inner: 2,
		nested: [1, 2, 3]
	)
)
```

## Supported File Types
- `.sc` - SuperCollider source files
- `.scd` - SuperCollider document files

## Notes
- The original source code structure is preserved
- Only whitespace, tabs, and newlines are modified
- String literals and characters are handled correctly
- The tool is conservative - it won't modify anything unless necessary

## Exit Codes
- `0` - Successful formatting
- `1` - Error (e.g., bracket mismatch or file not found)

