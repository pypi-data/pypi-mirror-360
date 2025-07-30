# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import typing
from pathlib import Path

import frontmatter
import msgspec

from .models import Document, Section


def load_document(file: typing.IO):
    return msgspec.yaml.decode(file.read(), type=Document)


def build_page(text: str) -> str:
    metadata, content = frontmatter.parse(text)
    return "# {}\n\n{}".format(metadata["title"], content).rstrip()


def build_section(doc_dir: Path, section: Section) -> str:
    return build_page(open(doc_dir / section.file).read())


def build_document(doc_dir: Path, document: Document) -> str:
    output = "\n\n".join(
        [build_section(doc_dir, section) for section in document.sections]
    )
    text = frontmatter.Post(output, title=document.title, version=document.version)
    return frontmatter.dumps(text) + "\n"
