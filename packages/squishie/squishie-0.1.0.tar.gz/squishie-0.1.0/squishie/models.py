# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import msgspec


class Section(msgspec.Struct, frozen=True):
    file: str


class Document(msgspec.Struct, frozen=True):
    title: str
    version: str

    metadata: dict[str, str] = msgspec.field(default_factory=dict)

    sections: list[Section] = msgspec.field(default_factory=list)
