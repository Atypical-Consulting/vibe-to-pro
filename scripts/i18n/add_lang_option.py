# -*- coding: utf-8 -*-
"""Rebuild every page's <select class="lang-switch"> from languages.json so
it lists every declared language, each option pointing at the correct
relative path from that page's own directory.

Run this once after adding a new language's page directory (or any time
languages.json changes) to propagate the new <option> to ALL existing pages,
in every language -- not just the new one's own pages.

Usage: python add_lang_option.py
"""
import glob
import json
import os
import re

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..", "..", "docs")
LANGS_PATH = os.path.join(HERE, "languages.json")
SELECT_RE = re.compile(r'<select class="lang-switch"[^>]*>.*?</select>', re.DOTALL)

SKIP_FILES = {"cours.html", "og-image.html"}


def load_languages():
    with open(LANGS_PATH, encoding="utf-8") as f:
        return json.load(f)


def rel_path(from_dir, to_dir, cid):
    if from_dir == to_dir:
        return f"{cid}.html"
    prefix = "../" if from_dir else ""
    to_seg = f"{to_dir}/" if to_dir else ""
    return f"{prefix}{to_seg}{cid}.html"


def build_select(langs, current_lang, cid):
    aria = langs[current_lang].get("aria", "Language")
    opts = []
    for code, info in langs.items():
        href = rel_path(langs[current_lang]["dir"], info["dir"], cid)
        selected = " selected" if code == current_lang else ""
        opts.append(f'<option value="{href}"{selected}>{info["label"]}</option>')
    return f'<select class="lang-switch" aria-label="{aria}">' + "".join(opts) + "</select>"


def page_dir_and_cid(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    parts = rel.split("/")
    cid = parts[-1][: -len(".html")]
    subdir = parts[0] if len(parts) > 1 else ""
    return subdir, cid


def main():
    langs = load_languages()
    dir_to_lang = {info["dir"]: code for code, info in langs.items()}
    changed = skipped = 0
    for path in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        if os.path.basename(path) in SKIP_FILES:
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()
        if 'class="lang-switch"' not in html:
            continue
        subdir, cid = page_dir_and_cid(path)
        lang = dir_to_lang.get(subdir)
        if lang is None:
            print("SKIP (dir not in languages.json):", path)
            skipped += 1
            continue
        new_select = build_select(langs, lang, cid)
        html2, n = SELECT_RE.subn(lambda _m: new_select, html, count=1)
        if n == 0:
            print("SKIP (no <select class=lang-switch> found):", path)
            skipped += 1
            continue
        if html2 != html:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html2)
            changed += 1
    print(f"{changed} files updated, {skipped} skipped. Languages: {', '.join(langs)}")


if __name__ == "__main__":
    main()
