# -*- coding: utf-8 -*-
"""Generic, structure-agnostic translation helper for the docs/*.html pages.

Walks the HTML with the stdlib parser, skipping <script>/<style>/<code>/<pre>
(commands and code samples must never be translated), and records every real
text node by exact byte offset in the source file. Only the trimmed text is
extracted -- surrounding whitespace/indentation is left untouched on inject.

Usage:
  python extract_text.py extract  docs/prologue.html        units.json
  python extract_text.py inject   docs/prologue.html units.json  docs/es/prologue.html

units.json shape: {"t0": "text", "t1": "text", ...} in document order.
Translate the VALUES (never add/remove/rename keys) and pass the result to inject.
"""
import json
import re
import sys
from html.parser import HTMLParser

SKIP_TAGS = {"script", "style", "code", "pre", "option"}
HAS_LETTER = re.compile(r"[^\W\d_]", re.UNICODE)


class TextSpanCollector(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.raw = raw
        self.line_offsets = self._line_offsets(raw)
        self.skip_depth = 0
        self.spans = []  # list of (start, end) into self.raw, trimmed

    @staticmethod
    def _line_offsets(raw):
        offsets = [0]
        for line in raw.splitlines(keepends=True):
            offsets.append(offsets[-1] + len(line))
        return offsets

    def _abs_pos(self):
        line, col = self.getpos()
        return self.line_offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth > 0 or not HAS_LETTER.search(data):
            return
        start = self._abs_pos()
        end = start + len(data)
        lead = len(data) - len(data.lstrip())
        trail = len(data) - len(data.rstrip())
        self.spans.append((start + lead, end - trail))


def extract(html_path, units_out_path):
    with open(html_path, encoding="utf-8") as f:
        raw = f.read()
    p = TextSpanCollector(raw)
    p.feed(raw)
    units = {f"t{i}": raw[s:e] for i, (s, e) in enumerate(p.spans)}
    with open(units_out_path, "w", encoding="utf-8") as f:
        json.dump(units, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(units)} text units from {html_path} -> {units_out_path}")


def inject(html_path, units_path, out_path):
    with open(html_path, encoding="utf-8") as f:
        raw = f.read()
    with open(units_path, encoding="utf-8") as f:
        units = json.load(f)
    p = TextSpanCollector(raw)
    p.feed(raw)
    if len(p.spans) != len(units):
        raise SystemExit(
            f"Span count mismatch: source has {len(p.spans)} units, "
            f"units file has {len(units)}. Re-extract from the CURRENT "
            f"source file before injecting (the page must not have changed "
            f"structurally since extraction)."
        )
    out = []
    cursor = 0
    for i, (start, end) in enumerate(p.spans):
        out.append(raw[cursor:start])
        out.append(units[f"t{i}"])
        cursor = end
    out.append(raw[cursor:])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(out))
    print(f"Injected {len(p.spans)} units -> {out_path}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "extract":
        extract(sys.argv[2], sys.argv[3])
    elif mode == "inject":
        inject(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        raise SystemExit("usage: extract_text.py extract|inject ...")
