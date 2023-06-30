from pprint import pprint
from dateutil import parser
import json
import re

"""
There are many things I would improve here. Error handling is poor. The final output could be normalised to be
more useful (for example, we could split registration date and plan ref into two fields, if such a thing is useful).

There are several assumptions here that are liable to break in some cases, but I think I've at least acknowledged them.
The biggest area of difficulty is in processing the last row of the entry (excluding notes). I solved this with
basically guessing based on what the value looks like. This is rarely a sustainable approach, but it's all I had time
for.
"""

EntryText = list[str]
Notes = list[str]

# This type is just there to communicate the expected format. It doesn't enforce the absence of notes.
EntryTextWithoutNotes = list[str]

COL_WIDTHS = [14, 26, 14, 11]
SEPARATOR_LENGTH = 2
ROW_LENGTH = 73


def is_first_line_of_note(row: str) -> bool:
    return bool(re.search("^[A-Z]+( [0-9]+)?:", row))


def extract_notes(entry_text: EntryText) -> [EntryTextWithoutNotes, Notes]:
    entry_text_without_notes = []

    i = 0
    while i < len(entry_text) and not is_first_line_of_note(entry_text[i]):
        entry_text_without_notes.append(entry_text[i])
        i += 1

    note_rows = entry_text[len(entry_text_without_notes):]

    notes = []
    # This slightly hacky negative index initialisation assumes that the first row is a note starting line.
    # The code that produced the node_rows above _should_ guarantee this, but we don't handle the exception
    # well if it doesn't :(
    current_note_index = -1
    for idx, row in enumerate(note_rows):
        if is_first_line_of_note(row):
            current_note_index += 1
            notes.append(row)
            continue
        notes[current_note_index] += f' {row}'

    return [entry_text_without_notes, notes]


# Pads rows to restore missing columns at the start.
# DOES NOT WORK FOR THE FINAL ROW, WHICH HAS ITS OWN RULES!
def pad_row(non_final_row: str):
    # This relies on the assumption that where non-final rows are missing columns, they are missing them from the start.
    # This is true in all cases that I could find, but it's still a potential bug.
    # As for the final row, all bets are off because it has so many edge cases.
    return " " * (ROW_LENGTH - len(non_final_row)) + non_final_row


def to_columns(entry_text: EntryTextWithoutNotes) -> list[str]:
    if not len(entry_text):
        # This is slightly misleading, since a row of empty strings isn't identical to no data at all.
        # In the context of this script, this just means we get empty strings in our output json fields,
        # which is fine for now.
        return ["", "", "", ""]

    *rest, last = entry_text  # the last row is problematic, so we'll handle it differently

    if not len(rest):
        return row_to_values(last)

    result = [""] * 4

    # appends each value from a row to its respective column
    def add_to_result(values: list[str]):
        for idx, value in enumerate(values):
            result[idx] += f' {value}'

    for row in rest:
        add_to_result(row_to_values(row))

    add_to_result(last_row_to_values(last))

    return [r.strip() for r in result]


def row_to_values(row: str) -> list[str]:
    result = [""] * 4

    padded = pad_row(row)
    current_position = 0
    for idx, column_width in enumerate(COL_WIDTHS):
        value = padded[current_position:current_position + column_width + SEPARATOR_LENGTH]
        result[idx] += value.strip()
        current_position += column_width + SEPARATOR_LENGTH
    return result


# The last row is problematic in several ways. See the tests for edge cases.
# This function does not pass all tests. Handling all the edge cases would take significantly longer
# than this exercise allows for. At least much of the edge-case madness is contained in this function,
# which is a clear candidate for improvement.
def last_row_to_values(row: str) -> list[str]:
    if len(row) == len(row.strip()):
        # Either first or third column value
        try:
            parser.parse(row.split(" ")[-1])
        except parser.ParserError:
            # The value doesn't end in a date, so it's _probably_ the first column
            return [row] + [""] * 3
        # The value ends in a date, so it's _probably_ the third column
        return ["", "", row, ""]

    # Fails when missing lessee
    if len(row) > COL_WIDTHS[0] + COL_WIDTHS[1]:
        return row_to_values(row)

    return ["", "", "", ""]


def main():
    with open('schedule_of_notices_of_lease_examples.json') as f:
        d = json.load(f)

    result = []
    for lease in d:
        entries = lease['leaseschedule']['scheduleEntry']
        for e in entries:
            text = e['entryText']
            if not text:
                continue
            try:
                clean = [t for t in text if t]  # remove null
                without_notes, notes = extract_notes(clean)
                columns = to_columns(without_notes)
                result.append({
                    'registrationDateAndPlanRef': columns[0],
                    'propertyDescription': columns[1],
                    'dateOfLeaseAndTerm': columns[2],
                    'lesseesTitle': columns[3],
                    'notes': notes
                })
            except Exception:
                # This is not good error handling for several reasons, but it at least allows us to process what we can.
                # If all fail for some code mistake, expect a lot of console output. Sorry :(
                print("FAILED:")
                pprint(e)

    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
