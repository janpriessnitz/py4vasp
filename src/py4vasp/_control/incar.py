# Copyright © VASP Software GmbH,
# Licensed under the Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
from py4vasp._control import base


class INCAR(base.InputFile):
    """The INCAR file defining the input parameters of a VASP calculation.

    Parameters
    ----------
    path : str or Path
        Defines where the INCAR file is stored. If set to None, the file will be kept
        in memory.
    """


def parse_incar_to_dict(text):
    return dict(_generate_tags(text))


def _generate_tags(text):
    for line in text.splitlines():
        line_without_comments, *_ = line.split("#")
        tag, separator, value = line_without_comments.partition("=")
        if separator:
            yield tag.strip().upper(), value.strip()
