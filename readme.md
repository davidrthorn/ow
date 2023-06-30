# "Schedule of notices of lease" parsing exercise

Parses the land registry _Schedule of notices of lease_ JSON output to a sensible format.

## Example usage

```bash
# assuming python3
pip install -r requirements.txt

# read in the file schedule_of_notices_of_lease_examples.json and produce output.json
python main.py

# tests (3 known failures -- see test code comments for details)
python test_main.py
```

## Limitations and improvements

These are found in the code in the form of notes, where they make more sense.
