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
1. **Empty Lines**: Keeps at most 2 consecutive empty lines outside bracketed blocks and 1 inside
2. **Whitespace**: Trims trailing whitespace and normalizes redundant spacing without changing string contents
3. **Redundant Semicolons**: Collapses repeated `;` characters in code to one. Repeated semicolons are rejected by sclang; semicolons in strings and comments are left unchanged
4. **Comments Preserved**:
   - Line comments (`//`) retain their text and are indented with the code
   - Block comments (`/* ... */`) are preserved exactly as-is and are not indented
5. **Indentation**: Uses tab characters for indentation, following sclang conventions similar to JavaScript and C#
6. **Bracket Validation**: Verifies all bracket pairs are properly matched:
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
- The formatter preserves source tokens except for collapsing repeated semicolons outside strings and comments
- String literals and block-comment contents are preserved exactly
- Line-comment text is retained; leading indentation and trailing whitespace are normalized
- Formatting is idempotent: formatting an already formatted file does not change it

## Exit Codes
- `0` - Successful formatting
- `1` - Error (e.g., bracket mismatch or file not found)

