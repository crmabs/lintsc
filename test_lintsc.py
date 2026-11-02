import unittest

from lintsc import BracketMismatchError, LintSc


class LintScTests(unittest.TestCase):
    def test_formatting_removes_redundant_semicolons_and_whitespace(self):
        source = '(\n    var value = 1;;;   \n\n\n    value.postln;\n)'
        expected = '(\n\tvar value = 1;\n\n\tvalue.postln;\n)'

        formatter = LintSc()
        formatter.validate_brackets(source)

        self.assertEqual(formatter.format_content(source), expected)

    def test_repeated_semicolons_are_cleaned_around_inline_block_comments(self):
        source = 'value;;; /* keep  spaces */\n'
        expected = 'value; /* keep  spaces */\n'

        self.assertEqual(LintSc().format_content(source), expected)

    def test_supercollider_character_literals_preserve_whitespace_and_brackets(self):
        source = 'call($ ); call($));'

        formatter = LintSc()
        formatter.validate_brackets(source)

        self.assertEqual(formatter.format_content(source), source)
        self.assertEqual(formatter.format_content('$ '), '$ ')

    def test_formatting_preserves_strings_and_comments(self):
        source = (
            '" two  spaces ;; and \\\" ( bracket";   // comment ;;  \n'
            '/* block  comment ;;\n   preserve this */\n'
        )
        expected = (
            '" two  spaces ;; and \\\" ( bracket"; // comment ;;\n'
            '/* block  comment ;;\n   preserve this */\n'
        )

        self.assertEqual(LintSc().format_content(source), expected)

    def test_blank_line_limits_differ_inside_and_outside_brackets(self):
        self.assertEqual(LintSc().format_content('a\n\n\n\nb'), 'a\n\n\nb')
        self.assertEqual(LintSc().format_content('(\na\n\n\nb\n)'), '(\n\ta\n\n\tb\n)')

    def test_indentation_tracks_brackets_and_is_idempotent(self):
        source = '(\n  [\n1,\n2\n]\n)\n'
        expected = '(\n\t[\n\t\t1,\n\t\t2\n\t]\n)\n'
        formatter = LintSc()

        formatted = formatter.format_content(source)
        self.assertEqual(formatted, expected)
        self.assertEqual(formatter.format_content(formatted), expected)

    def test_brackets_in_escaped_strings_and_comments_are_ignored(self):
        source = r'"escaped \" ( [ { ] ) }" // ([)]' + '\n(foo)'

        LintSc().validate_brackets(source)

    def test_bracket_validation_resets_state_for_each_call(self):
        formatter = LintSc()
        formatter.validate_brackets('([{}])')

        with self.assertRaises(BracketMismatchError):
            formatter.validate_brackets(')')

        formatter.validate_brackets('[]')

    def test_bracket_mismatch_reports_location(self):
        with self.assertRaises(BracketMismatchError) as error:
            LintSc().validate_brackets('([)]')

        self.assertIn("Line 1, Column 3", str(error.exception))
        self.assertIn("Found ')' but expected ']'", str(error.exception))


if __name__ == '__main__':
    unittest.main()
