#!/usr/bin/env python3
"""
Obsidian Vault Quality Score
Outputs details then a final integer: lower is better.
Score = broken_wikilinks + stub_notes + untagged_notes + orphan_notes

Usage: python3 vault_quality_score.py [--verbose]
"""

import os
import re
import sys

VAULT = os.path.expanduser("~/Documents/Obsidian/Obsidian")
STUB_WORD_THRESHOLD = 100
VERBOSE = "--verbose" in sys.argv

# System-generated folders that mirror the database — skip for quality scoring
SKIP_PREFIXES = (
    "Samaritan/Tasks/",
    "Samaritan/Goals/",
)


def get_all_notes():
    """Return dict of {stem_lower: filepath} for all .md files."""
    notes = {}
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                stem = os.path.splitext(f)[0].lower()
                notes[stem] = path
    return notes


def parse_note(path):
    """Return (tags, body_text, wikilinks)."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        content = fh.read()

    tags = []
    body = content

    # Extract YAML frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            fm = content[3:end]
            body = content[end + 3 :]

            # Block tags (YAML list):  tags:\n  - foo
            tag_block = re.search(
                r"^tags:\s*\n((?:[ \t]+[-•]\s*.+\n?)*)", fm, re.MULTILINE
            )
            if tag_block:
                tags = re.findall(r"[-•]\s*(.+)", tag_block.group(1))
            else:
                # Inline tags:  tags: [foo, bar]  or  tags: foo
                inline = re.search(r"^tags:\s*(.+)$", fm, re.MULTILINE)
                if inline:
                    raw = inline.group(1).strip()
                    if raw.startswith("["):
                        tags = [
                            t.strip().strip("\"'")
                            for t in raw.strip("[]").split(",")
                            if t.strip()
                        ]
                    elif raw:
                        tags = [raw.strip().strip("\"'")]

    # Extract all [[wikilinks]] (ignore aliases and anchors)
    wikilinks = re.findall(r"\[\[([^\]|#\n]+?)(?:[|#][^\]\n]*)?\]\]", content)

    return tags, body, wikilinks


def count_words(text):
    return len(text.split())


def main():
    all_notes = get_all_notes()
    note_stems = set(all_notes.keys())

    broken_link_detail = []
    stub_detail = []
    untagged_detail = []
    orphan_detail = []

    # First pass: collect all link targets across the vault
    linked_stems = set()
    note_data = {}  # stem -> (rel, tags, body, wikilinks)
    for stem, path in all_notes.items():
        rel = os.path.relpath(path, VAULT)
        tags, body, wikilinks = parse_note(path)
        note_data[stem] = (rel, tags, body, wikilinks)
        for link in wikilinks:
            link_stem = link.strip().lower().split("/")[-1]
            linked_stems.add(link_stem)

    # Second pass: score each note
    for stem, (rel, tags, body, wikilinks) in note_data.items():
        if any(rel.startswith(p) for p in SKIP_PREFIXES):
            continue

        # Untagged check
        if not tags:
            untagged_detail.append(rel)

        # Broken wikilinks
        for link in wikilinks:
            link_stem = link.strip().lower().split("/")[-1]
            if link_stem not in note_stems:
                broken_link_detail.append(f"{rel} → [[{link}]]")

        # Stub: under threshold words AND no outgoing links
        word_count = count_words(body)
        if word_count < STUB_WORD_THRESHOLD and not wikilinks:
            stub_detail.append(f"{rel} ({word_count}w)")

        # Orphan: no other note links to this one
        if stem not in linked_stems:
            orphan_detail.append(rel)

    broken = len(broken_link_detail)
    stubs = len(stub_detail)
    untagged = len(untagged_detail)
    orphans = len(orphan_detail)
    total = broken + stubs + untagged + orphans

    if VERBOSE:
        if broken_link_detail:
            print("BROKEN LINKS:")
            for item in broken_link_detail:
                print(f"  {item}")
        if stub_detail:
            print("STUBS:")
            for item in stub_detail:
                print(f"  {item}")
        if untagged_detail:
            print("UNTAGGED:")
            for item in untagged_detail:
                print(f"  {item}")
        if orphan_detail:
            print("ORPHANS:")
            for item in sorted(orphan_detail):
                print(f"  {item}")
        print()

    print(
        f"broken_links={broken} stub_notes={stubs} untagged_notes={untagged} orphan_notes={orphans} total={total}"
    )
    # Final line is the parseable metric
    print(total)


if __name__ == "__main__":
    main()
