# Copyright © VASP Software GmbH,
# Licensed under the Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
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
_OPEN = re.compile(r"\s*(?P<group>[\w/]+)\s*{\s*(?P<inner>.*\S)\s*")


def parse_incar_to_dict(text):
    return dict(_generate_tags(text))


def _generate_tags(text):
    for line in text.splitlines():
        line_without_comments, *_ = re.split("[#!]", line, maxsplit=1)
        for definition in line_without_comments.split(";"):
            yield from _parse_definition(definition, group="")


def _parse_definition(definition, group):
    open = _OPEN.match(definition)
    if open:
        group = f"{group}{open['group']}/"
        yield from _parse_definition(open["inner"], group)
        return
    assignment = _ASSIGNMENT.match(definition)
    if assignment:
        tag = f"{group}{assignment.group('tag')}".upper()
        value = assignment.group("value").rstrip(" }")
        yield tag, value
