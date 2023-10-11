# Copyright © VASP Software GmbH,
# Licensed under the Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
import pytest

from py4vasp._control.incar import parse_incar_to_dict
from py4vasp.control import INCAR

from .test_base import AbstractTest


class TestIncar(AbstractTest):
    tested_class = INCAR


@pytest.mark.parametrize(
    "input, output",
    [
        ("# empty file", {}),
        ("tag1 = value1 \n tag2 = value2", {"TAG1": "value1", "TAG2": "value2"}),
        (
            """first = tag
            # separated by comment from
            second = one""",
            {"FIRST": "tag", "SECOND": "one"},
        ),
        ("# TAG = bash-style comment\n! TAG2 = fortran-style comment", {}),
        (
            """# semicolon ; in = comment
            # open { or = close } in comment
            tag = value""",
            {"TAG": "value"},
        ),
        # (
        #     """ignore = inline # bash comment
        #     also = ignore ! inline fortran comment
        #     and { ! ignore comment
        #        after = open
        #     } # or = close""",
        #     {"IGNORE": "inline", "ALSO": "ignore", "AND/AFTER" : "open"},
        # ),
        ("first=1;second=2", {"FIRST": "1", "SECOND": "2"}),
        ("first = present # ; commented = out", {"FIRST": "present"}),
        ("second = tag ; ! commented = out", {"SECOND": "tag"}),
        ("comment # = in middle ; of = line", {}),
    ],
)
def test_from_string(input, output):
    assert parse_incar_to_dict(input) == output
