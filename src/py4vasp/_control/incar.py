# Copyright © VASP Software GmbH,
# Licensed under the Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
import dataclasses
import re

from py4vasp._control import base


class INCAR(base.InputFile):
    """The INCAR file defining the input parameters of a VASP calculation.

    Parameters
    ----------
    path : str or Path
        Defines where the INCAR file is stored. If set to None, the file will be kept
        in memory.
    """


TAGS = {}

_whitespace = r"\s*"
_optional = lambda regex: f"{regex}?"
_name = lambda label: r"(?P<{label}>[\w/]+)".format(label=label)
_value = r"(?P<inner>.*\S)"
_non_escaped = lambda char: r"((?<!\\){char}|(?<=\\\\){char})".format(char=char)
_non_quote = r'(?P<inner>(\\\"|[^"])*)'
_COMMENT = re.compile(_non_escaped("[#!]"))
_INLINE = re.compile(_non_escaped(";"))
_ESCAPED = re.compile(r"\\(?P<char>[=;#!{}\"\\])")
_NEWLINES = re.compile(r"(?<!\\)\r?\n")
_ESCAPED_NEWLINE = re.compile(_whitespace + r"\\\r?\n" + _whitespace)
_ASSIGNMENT = re.compile(
    _whitespace
    + _name("tag")
    + _whitespace
    + _non_escaped("=")
    + _whitespace
    + _value
    + _whitespace
)
_BEGIN_MULTILINE = re.compile(
    _whitespace
    + _name("tag")
    + _whitespace
    + _non_escaped("=")
    + _whitespace
    + _non_escaped('"')
    + _non_quote
)
_END_MULTILINE = re.compile(_non_quote + _non_escaped('"') + _whitespace)
_OPEN = re.compile(
    _whitespace
    + _name("group")
    + _whitespace
    + _non_escaped("{")
    + _whitespace
    + _optional(_value)
    + _whitespace
)
_CLOSE = re.compile(
    _whitespace + _optional(_value) + _whitespace + _non_escaped("}") + _whitespace
)


def parse_incar_to_dict(text):
    return dict(_generate_tags(text))


def _generate_tags(text):
    parser = _Parser()
    for line in _NEWLINES.split(text):
        if parser.multiline:
            yield from parser.parse_multiline(line)
        else:
            yield from parser.parse_line(line)


@dataclasses.dataclass
class _Parser:
    group: str = ""
    depth: list = dataclasses.field(default_factory=list)
    multiline: str = ""
    content: list = dataclasses.field(default_factory=list)

    def parse_multiline(self, line):
        end_multiline = _END_MULTILINE.match(line)
        if end_multiline:
            self.content.append(end_multiline["inner"])
            yield self.multiline, self.remove_escape("\n".join(self.content))
            self.multiline = ""
            self.content = []
        else:
            self.content.append(line)

    def parse_line(self, line):
        multiline = _BEGIN_MULTILINE.match(line)
        if multiline:
            self.multiline = self.tagname(multiline)
            yield from self.parse_multiline(multiline["inner"])
        else:
            line = _ESCAPED_NEWLINE.sub(" ", line)
            line_without_comments, *_ = _COMMENT.split(line, maxsplit=1)
            for definition in _INLINE.split(line_without_comments):
                yield from self.parse_definition(definition)

    def parse_definition(self, definition):
        open = _OPEN.match(definition)
        if open:
            self.group = f"{self.group}/{open['group']}"
            self.depth.append(open["group"].count("/") + 1)
            if open["inner"]:
                yield from self.parse_definition(open["inner"])
            return
        close = _CLOSE.match(definition)
        if close:
            if close["inner"]:
                yield from self.parse_definition(close["inner"])
            depth = self.depth.pop()
            for _ in range(depth):
                self.group, *_ = self.group.rpartition("/")
            return
        assignment = _ASSIGNMENT.match(definition)
        if assignment:
            yield self.tagname(assignment), self.remove_escape(assignment["inner"])

    def tagname(self, match):
        return f"{self.group}/{match['tag']}".lstrip("/").upper()

    def remove_escape(self, text):
        return _ESCAPED.sub(r"\g<char>", text)
