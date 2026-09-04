# -*- coding: utf-8 -*-
"""Find every place in docs/ that cites a number/date from site-meta.json.

Run once BEFORE touching any file: this is the full checklist of citation
sites for the CURRENT figures. After bumping site-meta.json to the new
numbers and editing those sites, run again pointing at a saved copy of the
OLD site-meta.json (git show HEAD:scripts/refresh/site-meta.json > /tmp/old.json)
-- zero hits means nothing was missed.

Usage:
  python find_stale_numbers.py [path/to/site-meta.json]
"""
import glob
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..", "..", "docs")

FR_MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
             "juil.", "août", "sept.", "oct.", "nov.", "déc."]
EN_MONTHS = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]


def date_variants(iso_date):
    y, m, d = (int(x) for x in iso_date.split("-"))
    return {iso_date, f"{d} {FR_MONTHS[m - 1]} {y}", f"{EN_MONTHS[m - 1]} {d}, {y}"}


def main():
    meta_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "site-meta.json")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    needles = {
        str(meta["last_version"]): "last_version",
        f'v{meta["last_version"]}': "last_version",
        str(meta["versions_analyzed"]): "versions_analyzed",
        str(meta["candidate_features"]): "candidate_features",
        str(meta["confirmed_or_updated"]): "confirmed_or_updated",
        str(meta["kept_facts"]): "kept_facts",
    }
    for v in date_variants(meta["verified_date"]):
        needles[v] = "verified_date"

    patterns = {re.compile(r"(?<!\d)" + re.escape(n) + r"(?!\d)"): field for n, field in needles.items()}

    hits = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                seen_fields = set()
                for pat, field in patterns.items():
                    if field in seen_fields:
                        continue
                    if pat.search(line):
                        seen_fields.add(field)
                        rel = os.path.relpath(path, ROOT)
                        print(f"{rel}:{lineno}: [{field}] {line.strip()[:130]}")
                        hits += 1
    print(f"\n{hits} citation(s) found against {meta_path}")


if __name__ == "__main__":
    main()
