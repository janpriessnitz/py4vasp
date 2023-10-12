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


_whitespace = r"\s*"
_optional = lambda regex: f"{regex}?"
_name = lambda label: r"(?P<{label}>[\w/]+)".format(label=label)
_value = lambda label: r"(?P<{label}>.*\S)".format(label=label)
_non_escaped = lambda char: r"((?<!\\){char}|(?<=\\\\){char})".format(char=char)
_ASSIGNMENT = re.compile(
    _whitespace
    + _name("tag")
    + _whitespace
    + _non_escaped("=")
    + _whitespace
    + _value("value")
    + _whitespace
)
_COMMENT = re.compile(_non_escaped("[#!]"))
_INLINE = re.compile(_non_escaped(";"))
_OPEN = re.compile(
    _whitespace
    + _name("group")
    + _whitespace
    + _non_escaped("{")
    + _whitespace
    + _optional(_value("inner"))
    + _whitespace
)
_CLOSE = re.compile(
    _whitespace
    + _optional(_value("inner"))
    + _whitespace
    + _non_escaped("}")
    + _whitespace
)
_ESCAPED = re.compile(r"\\(?P<char>[=;#!{}])")


def parse_incar_to_dict(text):
    return dict(_generate_tags(text))


def _generate_tags(text):
    parser = _Parser()
    for line in text.splitlines():
        line_without_comments, *_ = _COMMENT.split(line, maxsplit=1)
        for definition in _INLINE.split(line_without_comments):
            yield from parser._parse_definition(definition)


@dataclasses.dataclass
class _Parser:
    group: str = ""
    depth: list = dataclasses.field(default_factory=list)

    def _parse_definition(self, definition):
        open = _OPEN.match(definition)
        if open:
            self.group = f"{self.group}/{open['group']}"
            self.depth.append(open["group"].count("/") + 1)
            if open["inner"]:
                yield from self._parse_definition(open["inner"])
            return
        close = _CLOSE.match(definition)
        if close:
            if close["inner"]:
                yield from self._parse_definition(close["inner"])
            depth = self.depth.pop()
            for _ in range(depth):
                self.group, *_ = self.group.rpartition("/")
            return
        assignment = _ASSIGNMENT.match(definition)
        if assignment:
            tag = f"{self.group}/{assignment.group('tag')}".lstrip("/").upper()
            value = assignment.group("value").rstrip(" }")
            value = _ESCAPED.sub(r"\g<char>", value)
            yield tag, value
