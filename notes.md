# The Data
## What we know

The first string is predictable. It contains:

1. Registration date
2. Beginning of the address
3. Date of lease
4. Lessee's title

---
The data can have missing columns, causing column misalignment.
But I don't think it can have any columns missing. It 
appears that if the first column is missing, the whole thing
can be shifted to the left. But if a central column is missing,
there is white space.

There is also usually a final column containing the Lessee Title,
even if it's empty. This allows us to align right. However, this
isn't always present, so we could detect it (quite easily) when there
is text (it's either the right format, or it's "registered" as part
of "Not registered").

---

Notes start with NOTE and can run multiple lines. They are always at the end.

---

We want the best balance of generality, simplicity and flexibility.

---
I can't see any double spaces that aren't column gaps, or any single
spaces that are -- but this is a dangerous assumption.

---
A single line that is a sentence is a note. Starts with UPPERCASE, but maybe not
NOTE.

# Possible Approaches

1. Split into columns and shift columns right when missing first
    columns. Allow for empty columns. Spacing between columns
    appears to be 4-6 chars.
2. Try to determine the column based on the data in it.
3. Column widths: columns are a certain character width. This is helpful!
   1. 165 and 166 on
   2. Parking spaces 182 and 183
   3. 999 years from
   4. registered

# Pseudocode

1. Harvest any notes from the end of the array (they start with 'NOTE'). Find the first 'NOTE' and go from there.
2. If nothing left after note harvest, end.
3. Assemble the dictionary by adding row 1 fields to it.
4. Shift middle rows into correct columns:
   1. Big white spaces are columns.
   2. Align columns right.
5. Handle final row (difficult!)


# Follow up

Given the inevitable edge cases, what's the overall strategy? Keep building in if statements to
catch every edge case? Be satisfied with a percentage accuracy rather than perfection?

# To improve

There's a bunch of guess work and it's not very robust.

Integration/acceptance tests.

Error handling

Normalisation