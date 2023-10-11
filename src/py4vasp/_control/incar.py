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


_ASSIGNMENT = re.compile(r"\s*(?P<tag>[\w/]+)\s*=\s*(?P<value>.*\S)\s*")
_OPEN = re.compile(r"\s*(?P<group>[\w/]+)\s*{\s*(?P<inner>.*\S)?\s*")
_CLOSE = re.compile(r"\s*(?P<inner>.*)}\s*")


def parse_incar_to_dict(text):
    return dict(_generate_tags(text))


def _generate_tags(text):
    parser = _Parser()
    for line in text.splitlines():
        line_without_comments, *_ = re.split("[#!]", line, maxsplit=1)
        for definition in line_without_comments.split(";"):
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
            yield from self._parse_definition(close["inner"])
            depth = self.depth.pop()
            for _ in range(depth):
                self.group, *_ = self.group.rpartition("/")
            return
        assignment = _ASSIGNMENT.match(definition)
        if assignment:
            tag = f"{self.group}/{assignment.group('tag')}".lstrip("/").upper()
            value = assignment.group("value").rstrip(" }")
            yield tag, value
