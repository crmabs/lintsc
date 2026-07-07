#!/usr/bin/env python3
"""
LintSc - Supercollider sclang linter utility
Formats sclang source files written in Python
"""

import sys
import argparse
import os
from pathlib import Path


class BracketMismatchError(Exception):
    """Exception raised when bracket pairs don't match"""
    pass


class LintSc:
    """Main linter class for formatting sclang files"""
    
    def __init__(self):
        self.bracket_stack = []
        self.bracket_pairs = {'(': ')', '[': ']', '{': '}'}
        self.closing_brackets = {')', ']', '}'}
        self.bracket_positions = []  # Track position of each bracket
        self.in_block_comment = False
        self.block_comment_start_line = 0
        
    def validate_brackets(self, content):
        """Validate that all brackets are properly paired"""
        in_line_comment = False
        in_string = False
        string_char = None
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # Track block comments
            i = 0
            while i < len(line):
                # Check for string literals
                if not in_line_comment and not self.in_block_comment:
                    if line[i] in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            string_char = line[i]
                        elif line[i] == string_char:
                            in_string = False
                
                # Check for block comment start
                if not in_line_comment and not in_string and i < len(line) - 1:
                    if line[i:i+2] == '/*':
                        self.in_block_comment = True
                        self.block_comment_start_line = line_num
                        i += 2
                        continue
                
                # Check for block comment end
                if self.in_block_comment and i < len(line) - 1:
                    if line[i:i+2] == '*/':
                        self.in_block_comment = False
                        i += 2
                        continue
                
                # Check for line comment
                if not self.in_block_comment and not in_string and i < len(line) - 1:
                    if line[i:i+2] == '//':
                        in_line_comment = True
                        break
                
                # Check brackets only outside comments and strings
                if not in_line_comment and not self.in_block_comment and not in_string:
                    if line[i] in self.bracket_pairs:
                        self.bracket_stack.append((line[i], line_num, i+1))
                    elif line[i] in self.closing_brackets:
                        if not self.bracket_stack:
                            raise BracketMismatchError(
                                f"Line {line_num}, Column {i+1}: Unexpected closing bracket '{line[i]}'"
                            )
                        opening, start_line, start_col = self.bracket_stack.pop()
                        expected_closing = self.bracket_pairs[opening]
                        if line[i] != expected_closing:
                            raise BracketMismatchError(
                                f"Line {line_num}, Column {i+1}: Found '{line[i]}' but expected '{expected_closing}' "
                                f"(matching '{opening}' from line {start_line}, column {start_col})"
                            )
                
                i += 1
            
            in_line_comment = False
        
        if self.bracket_stack:
            opening, line_num, col = self.bracket_stack[0]
            raise BracketMismatchError(
                f"Line {line_num}, Column {col}: Unclosed bracket '{opening}'"
            )
    
    def get_indent_level(self, line, indent_level):
        """Determine indent level based on bracket content"""
        stripped = line.lstrip()
        
        # Closing brackets should be dedented
        if stripped and stripped[0] in ('}', ']', ')'):
            return max(0, indent_level - 1)
        
        return indent_level
    
    def count_indent_change(self, line):
        """Count how indent level should change after this line"""
        in_string = False
        string_char = None
        in_line_comment = False
        in_block_comment = False
        
        change = 0
        i = 0
        
        while i < len(line):
            # Track strings
            if line[i] in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = line[i]
                elif line[i] == string_char:
                    in_string = False
            
            # Track line comments
            if not in_string and not in_block_comment and i < len(line) - 1:
                if line[i:i+2] == '//':
                    in_line_comment = True
                    break
            
            # Track block comments
            if not in_string and not in_line_comment and i < len(line) - 1:
                if line[i:i+2] == '/*':
                    in_block_comment = True
                elif line[i:i+2] == '*/':
                    in_block_comment = False
                    i += 1
            
            # Count bracket changes (not in comments or strings)
            if not in_string and not in_line_comment and not in_block_comment:
                if line[i] in ('{', '[', '('):
                    change += 1
                elif line[i] in ('}', ']', ')'):
                    change -= 1
            
            i += 1
        
        return change
    
    def should_skip_indent(self, line):
        """Check if line should have indentation applied"""
        stripped = line.lstrip()
        
        # Don't format line comments (only indent)
        if stripped.startswith('//'):
            return False  # We should indent these
        
        # Block comments are handled specially
        return False
    
    def format_content(self, content):
        """Format the content according to linting rules"""
        lines = content.split('\n')
        formatted_lines = []
        indent_level = 0
        prev_empty_count = 0
        in_block_comment = False
        nof_lines=len(lines)

        for i, line in enumerate(lines):
            stripped = line.lstrip()
            
            if len(stripped.rstrip()) == 0 and i<nof_lines-1:
                kov_sor=lines[i+1].lstrip().rstrip();
                if '}' == kov_sor or '});' == kov_sor:
                    #print("nyomorult")
                    continue;
            # 
            #     print("nyomorult")
            #    
            #         continue;


            # Track block comments
            if '/*' in line and '*/' not in line:
                in_block_comment = True
            elif '*/' in line:
                in_block_comment = False
            
            # Handle block comments - don't indent them
            if in_block_comment or (line.strip().startswith('/*') and '*/' in line):
                formatted_lines.append(line)
                prev_empty_count += 1 if not stripped else 0
                continue
            
            # Handle empty lines
            if not stripped:
                # Keep max 2 empty lines outside functions, max 1 inside
                # For simplicity, we'll enforce max 2 consecutive empty lines
                if prev_empty_count < 2:
                    formatted_lines.append('')
                    prev_empty_count += 1
                continue
            
            prev_empty_count = 0
            
            # Determine indentation for this line
            current_indent = self.get_indent_level(stripped, indent_level)
            
            # Handle line comments - indent them like code
            if stripped.startswith('//'):
                formatted_lines.append('\t' * current_indent + stripped)
            else:
                # Regular code line - format it
                formatted_lines.append('\t' * current_indent + stripped)
            
            # Update indent level for next line based on brackets in current line
            indent_level += self.count_indent_change(line)
            indent_level = max(0, indent_level)
        
        return '\n'.join(formatted_lines)
    
    def process_file(self, input_file, output_file=None):
        """Process the input file and write output"""
        # Read input file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Validate brackets
        try:
            self.validate_brackets(content)
        except BracketMismatchError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Format content
        formatted_content = self.format_content(content)
        
        # Determine output file
        if output_file is None:
            # Add "f_" prefix to filename
            input_path = Path(input_file)
            output_file = input_path.parent / f"f_{input_path.name}"
        
        # Write output file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            print(f"Success: Formatted file written to '{output_file}'")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='LintSc - Supercollider sclang linter utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lintsc.py -in myfile.sc
  python3 lintsc.py -in myfile.scd -out formatted.scd
        """
    )
    
    parser.add_argument(
        '-in',
        dest='input_file',
        required=True,
        help='Input sclang source file (*.sc or *.scd)'
    )
    
    parser.add_argument(
        '-out',
        dest='output_file',
        default=None,
        help='Output file (default: f_<inputfile>)'
    )
    
    args = parser.parse_args()
    
    # Process file
    linter = LintSc()
    linter.process_file(args.input_file, args.output_file)


if __name__ == '__main__':
    main()

