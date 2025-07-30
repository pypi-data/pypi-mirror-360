# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from squishie.builder import build_document, load_document

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_load_document():
    document_file = FIXTURE_DIR / "minimal" / "squishie.yaml"
    document = load_document(open(document_file))
    assert document.title == "My squished document"
    assert document.version == "1.2.3"
    assert document.sections[0].file == "doc1.md"
    assert document.sections[1].file == "doc2.md"


def test_build_document():
    document_file = FIXTURE_DIR / "minimal" / "squishie.yaml"
    document = load_document(open(document_file))
    output = build_document(FIXTURE_DIR / "minimal", document)
    expected = """---
title: My squished document
version: 1.2.3
---

# Doc 1

This is some text.

# Doc 2

This is different text.
"""
    assert output == expected
