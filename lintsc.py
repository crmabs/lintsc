#!/usr/bin/env python3
"""
LintSc - Supercollider sclang linter utility
Formats sclang source files written in Python
"""

import sys
import argparse
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
        """Validate bracket pairs while ignoring strings and comments."""
        self.bracket_stack = []
        self.in_block_comment = False
        in_line_comment = False
        string_char = None
        escaped = False
        line_num = 1
        column = 1
        index = 0

        while index < len(content):
            char = content[index]
            pair = content[index:index + 2]

            if char == '\n':
                line_num += 1
                column = 1
                in_line_comment = False
                index += 1
                continue

            if in_line_comment:
                index += 1
                column += 1
                continue

            if self.in_block_comment:
                if pair == '*/':
                    self.in_block_comment = False
                    index += 2
                    column += 2
                else:
                    index += 1
                    column += 1
                continue

            if string_char is not None:
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == string_char:
                    string_char = None
                index += 1
                column += 1
                continue

            if pair == '//':
                in_line_comment = True
                index += 2
                column += 2
                continue
            if pair == '/*':
                self.in_block_comment = True
                self.block_comment_start_line = line_num
                index += 2
                column += 2
                continue
            if char == '$':
                index += 1
                column += 1
                if index < len(content) and content[index] != '\n':
                    if content[index] == '\\' and index + 1 < len(content) and content[index + 1] != '\n':
                        index += 2
                        column += 2
                    else:
                        index += 1
                        column += 1
                continue
            if char in ('"', "'"):
                string_char = char
            elif char in self.bracket_pairs:
                self.bracket_stack.append((char, line_num, column))
            elif char in self.closing_brackets:
                if not self.bracket_stack:
                    raise BracketMismatchError(
                        f"Line {line_num}, Column {column}: Unexpected closing bracket '{char}'"
                    )
                opening, start_line, start_col = self.bracket_stack.pop()
                expected_closing = self.bracket_pairs[opening]
                if char != expected_closing:
                    raise BracketMismatchError(
                        f"Line {line_num}, Column {column}: Found '{char}' but expected '{expected_closing}' "
                        f"(matching '{opening}' from line {start_line}, column {start_col})"
                    )

            index += 1
            column += 1

        if self.bracket_stack:
            opening, opening_line, opening_column = self.bracket_stack[0]
            raise BracketMismatchError(
                f"Line {opening_line}, Column {opening_column}: Unclosed bracket '{opening}'"
            )
    
    def get_indent_level(self, line, indent_level):
        """Determine indent level based on bracket content"""
        stripped = line.lstrip()
        
        # Closing brackets should be dedented
        if stripped and stripped[0] in ('}', ']', ')'):
            return max(0, indent_level - 1)
        
        return indent_level
    
    def _scan_line(self, line, state):
        """Return bracket changes and whether a line contains preserved text."""
        change = 0
        leading_closers = 0
        at_leading_code = True
        preserve_line = state['in_block_comment'] or state['string_char'] is not None
        index = 0

        while index < len(line):
            char = line[index]
            pair = line[index:index + 2]

            if state['in_block_comment']:
                if pair == '*/':
                    state['in_block_comment'] = False
                    index += 2
                else:
                    index += 1
                continue

            if state['string_char'] is not None:
                if state['escaped']:
                    state['escaped'] = False
                elif char == '\\':
                    state['escaped'] = True
                elif char == state['string_char']:
                    state['string_char'] = None
                index += 1
                continue

            if pair == '//':
                break
            if pair == '/*':
                state['in_block_comment'] = True
                preserve_line = preserve_line or at_leading_code
                index += 2
                continue
            if char == '$':
                at_leading_code = False
                index += 1
                if index < len(line):
                    if line[index] == '\\' and index + 1 < len(line):
                        index += 2
                    else:
                        index += 1
                continue
            if char in ('"', "'"):
                state['string_char'] = char
                state['escaped'] = False
                at_leading_code = False
            elif char in self.bracket_pairs:
                change += 1
                at_leading_code = False
            elif char in self.closing_brackets:
                change -= 1
                if at_leading_code:
                    leading_closers += 1
                else:
                    at_leading_code = False
            elif not char.isspace():
                at_leading_code = False

            index += 1

        if state['in_block_comment'] or state['string_char'] is not None:
            preserve_line = True
        return change, leading_closers, preserve_line

    def count_indent_change(self, line):
        """Count bracket changes on a line, ignoring strings and comments."""
        state = {'in_block_comment': False, 'string_char': None, 'escaped': False}
        change, _, _ = self._scan_line(line, state)
        return change
    
    def should_skip_indent(self, line):
        """Check if line should have indentation applied"""
        stripped = line.lstrip()
        
        # Don't format line comments (only indent)
        if stripped.startswith('//'):
            return False  # We should indent these
        
        # Block comments are handled specially
        return False
    
    @staticmethod
    def _clean_code_line(line):
        """Normalize redundant code whitespace and collapse empty statements."""
        output = []
        pending_space = False
        previous_code_char = None
        string_char = None
        escaped = False
        index = 0

        while index < len(line):
            char = line[index]
            pair = line[index:index + 2]

            if string_char is not None:
                output.append(char)
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == string_char:
                    string_char = None
                    previous_code_char = char
                index += 1
                continue

            if pair == '/*':
                if pending_space and output:
                    output.append(' ')
                pending_space = False
                comment_end = line.find('*/', index + 2)
                if comment_end == -1:
                    output.append(line[index:])
                    break
                output.append(line[index:comment_end + 2])
                index = comment_end + 2
                continue

            if pair == '//':
                if pending_space and output:
                    output.append(' ')
                output.append(line[index:].rstrip())
                break

            if char == '$':
                if pending_space and output:
                    output.append(' ')
                pending_space = False
                literal_end = index + 2
                if index + 1 < len(line) and line[index + 1] == '\\' and index + 2 < len(line):
                    literal_end = index + 3
                output.append(line[index:literal_end])
                previous_code_char = None
                index = literal_end
                continue

            if char in ('"', "'"):
                if pending_space and output:
                    output.append(' ')
                pending_space = False
                string_char = char
                output.append(char)
                previous_code_char = char
                index += 1
                continue

            if char.isspace():
                pending_space = True
                index += 1
                continue

            if char in ',;.)]}':
                pending_space = False
                if char == ';' and previous_code_char == ';':
                    index += 1
                    continue
                output.append(char)
                previous_code_char = char
                index += 1
                continue

            if char == '{' and previous_code_char == '}':
                pending_space = False
            elif char == '^' and previous_code_char == '{':
                output.append(' ')
                pending_space = False
            elif pending_space and output:
                output.append(' ')
                pending_space = False
            else:
                pending_space = False

            output.append(char)
            previous_code_char = char
            index += 1

        return ''.join(output)

    def format_content(self, content):
        """Format code while preserving literal and comment contents."""
        formatted_lines = []
        indent_level = 0
        empty_line_count = 0
        state = {'in_block_comment': False, 'string_char': None, 'escaped': False}

        for line in content.split('\n'):
            change, leading_closers, preserve_line = self._scan_line(line, state)

            if preserve_line:
                formatted_lines.append(line)
                empty_line_count = 0
            else:
                cleaned = self._clean_code_line(line).lstrip()
                if not cleaned:
                    max_empty_lines = 1 if indent_level else 2
                    if empty_line_count < max_empty_lines:
                        formatted_lines.append('')
                        empty_line_count += 1
                else:
                    current_indent = max(0, indent_level - leading_closers)
                    formatted_lines.append('\t' * current_indent + cleaned)
                    empty_line_count = 0

            indent_level = max(0, indent_level + change)

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

