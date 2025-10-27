#!/usr/bin/env python3
"""
Convert data/orginal_data_100.csv -> data/orginal_data_100_time.csv

Usage: run this from the repository root:
    python3 scripts/convert_orginal_to_time_csv.py

The script reads data/orginal_data_100.csv which contains a single column named "Position"
where each cell is a string representation of a list of [lon, lat] pairs (e.g. "[[lon, lat], [lon, lat], ...]").
It computes n = number of coordinates per trajectory and time = (n-1)*15, then writes
data/orginal_data_100_time.csv with two columns: trajectory_id (starting at 1) and time.
"""

import csv
import ast
import sys
from pathlib import Path

INPUT = Path("data/orginal_data_100.csv")
OUTPUT = Path("data/orginal_data_100_time.csv")

if not INPUT.exists():
    print(f"Input file {INPUT} not found. Run this script from the repository root.")
    sys.exit(1)

with INPUT.open(newline='\n', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader, None)  # skip header
    rows = list(reader)

out_rows = [("trajectory_id", "time")]
for i, row in enumerate(rows, start=1):
    if not row:
        # skip empty lines
        continue
    s = row[0].strip()
    # Remove surrounding quotes if present
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        s = s[1:-1]

    # Try to parse the string as Python literal (list of lists)
    n = 0
    try:
        coords = ast.literal_eval(s)
        if isinstance(coords, (list, tuple)):
            n = len(coords)
        else:
            n = 0
    except Exception:
        # Fallback: count separators '],[' which indicates coordinate boundaries
        if s:
            n = s.count('],[) + 1
        else:
            n = 0

    if n <= 0:
        time = 0
    else:
        time = (n - 1) * 15

    out_rows.append((i, time))

with OUTPUT.open('w', newline='\n', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(out_rows)

print(f"Wrote {len(out_rows)-1} trajectories to {OUTPUT}")