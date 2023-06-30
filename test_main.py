import unittest
from main import ROW_LENGTH, pad_row, to_columns, last_row_to_values, extract_notes, is_first_line_of_note

"""
I would have liked to write proper acceptance tests for this, but there wasn't time. Ideally, we'd have a bunch
of problematic, real-world examples to test against. This would help avoid regression significantly. As it is, there
are unit tests. There aren't enough of those really, but considering the length of the exercise...

There's a lot of boilerplate here and I think case-based testing would be easier to write and read.

FAILING TESTS: some of the last line parsing tests fail. These failures capture edge cases I didn't have time to
solve, but at least they are captured here. There are probably many more.
"""


class TestIsNoteFirstLine(unittest.TestCase):
    def test_single_note(self):
        self.assertTrue(is_first_line_of_note('NOTE: blah'))

    def test_numbered_note(self):
        self.assertTrue(is_first_line_of_note('NOTE 1: blah'))

    def test_numbered_other(self):
        self.assertTrue(is_first_line_of_note('HELLO 1: blah'))

    def test_non_note(self):
        self.assertFalse(is_first_line_of_note('This is not note first line'))


class TestExtractNotes(unittest.TestCase):

    def test_single_note(self):
        data = ["NOTE: blah blah blah"]
        entry, notes = extract_notes(data)
        self.assertEqual(data, notes)

    def test_multiple_notes(self):
        data = ["NOTE: one", "NOTE: two"]
        entry, notes = extract_notes(data)
        self.assertEqual(data, notes)

    def test_multiline_notes(self):
        data = ["NOTE 1: one", "uno", "eins", "NOTE 2: two", "duo"]
        entry, notes = extract_notes(data)
        self.assertEqual(["NOTE 1: one uno eins", "NOTE 2: two duo"], notes)

    def test_entry_with_note(self):
        data = [
            "16.03.2009      Jewson Stand, Coventry        01.12.2008      WM948282   ",
            "NOTE: blah blah blah"
        ]
        entry, notes = extract_notes(data)
        self.assertEqual(data[:1], entry)
        self.assertEqual(data[1:], notes)


class TestPadRow(unittest.TestCase):

    def test_result_is_correct_length(self):
        got = pad_row("cat")
        self.assertEqual(len(got), ROW_LENGTH)

    def test_padding_is_at_start(self):
        got = pad_row("cat")
        self.assertEqual(got[0], " ")
        self.assertEqual(got[-1], "t")


class TestToColumns(unittest.TestCase):

    def test_single_complete_row(self):
        data = "16.03.2009      Jewson Stand, Coventry        01.12.2008      WM948282   "
        got = to_columns([data])
        self.assertEqual(["16.03.2009", "Jewson Stand, Coventry", "01.12.2008", "WM948282"], got)

    def test_two_multiple_rows(self):
        data = "16.03.2009      Jewson Stand, Coventry        01.12.2008      WM948282   "
        got = to_columns([data])
        self.assertEqual(["16.03.2009", "Jewson Stand, Coventry", "01.12.2008", "WM948282"], got)


class TestLastRowToValues(unittest.TestCase):

    def test_complete_row(self):
        data = "edged and       and upper ground floors are   150 years                  "
        got = last_row_to_values(data)
        self.assertEqual(["edged and", "and upper ground floors are", "150 years", ""], got)

    def test_complete_row_with_only_first(self):
        data = "of)                                                                      "
        got = last_row_to_values(data)
        self.assertEqual(["of)", "", "", ""], got)

    # Fails because 'December' isn't date parseable by dateutils
    def test_paddable_last_row_third_only(self):
        data = "25 December                "
        got = last_row_to_values(data)
        self.assertEqual(["", "", "25 December", ""], got)

    def test_paddable_last_row_blank_lessee(self):
        data = "Street                        to 31.12.2112              "
        got = last_row_to_values(data)
        self.assertEqual(["", "Street", "to 31.12.2112", ""], got)

    def test_paddable_last_row_non_code_lessee(self):
        data = "Street                        to 31.12.2112   above      "
        got = last_row_to_values(data)
        self.assertEqual(["", "Street", "to 31.12.2112", "above"], got)

    def test_first_column_only(self):
        data = "of)"
        got = last_row_to_values(data)
        self.assertEqual(["of)", "", "", ""], got)

    # Fails because 1 is date parsable, which confuses my implementation
    def test_first_column_with_number(self):
        data = "plan 1"
        got = last_row_to_values(data)
        self.assertEqual(["plan 1", "", "", ""], got)

    def test_third_column_only(self):
        data = "30.8.2026"
        got = last_row_to_values(data)
        self.assertEqual(["", "", "30.8.2026", ""], got)

    def test_third_column_only_with_prefix(self):
        data = "to 30.8.2026"
        got = last_row_to_values(data)
        self.assertEqual(["", "", "to 30.8.2026", ""], got)

    # Fails because when there's no lessee, there's no reliable way to pad (that I've found).
    def test_missing_lessee(self):
        data = "4 (part of)                                   20.6.2006"
        got = last_row_to_values(data)
        self.assertEqual(["4 (part of)", "", "20.6.2006", ""], got)


if __name__ == '__main__':
    unittest.main()
