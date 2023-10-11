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
        (
            """ignore = inline # bash comment
            also = ignore ! inline fortran comment
            and { ! ignore comment
               after = open
            } # or = close""",
            {"IGNORE": "inline", "ALSO": "ignore", "AND/AFTER" : "open"},
        ),
        ("first=1;second=2", {"FIRST": "1", "SECOND": "2"}),
        ("first = present # ; commented = out", {"FIRST": "present"}),
        ("second = tag ; ! commented = out", {"SECOND": "tag"}),
        ("comment # = in middle ; of = line", {}),
        ("nested/tag=set inline", {"NESTED/TAG": "set inline"}),
        (
            """nested { tag = with inline delimiters }
            two { layers { of = nesting }}
            global = tag""",
            {
                "NESTED/TAG": "with inline delimiters",
                "TWO/LAYERS/OF": "nesting",
                "GLOBAL": "tag",
            },
        ),
        (
            """single {
                group = with
                more = than
                one = tag
            }
            nested {
                group = with
                multiple {
                    layers = and
                    tags { defined = within }
                    inline = statements ; are = possible
            }}""",
            {
                "SINGLE/GROUP": "with",
                "SINGLE/MORE": "than",
                "SINGLE/ONE": "tag",
                "NESTED/GROUP": "with",
                "NESTED/MULTIPLE/LAYERS": "and",
                "NESTED/MULTIPLE/TAGS/DEFINED": "within",
                "NESTED/MULTIPLE/INLINE": "statements",
                "NESTED/MULTIPLE/ARE": "possible",
            },
        ),
    ],
)
def test_from_string(input, output):
    import pprint

    pprint.pprint(parse_incar_to_dict(input))
    assert parse_incar_to_dict(input) == output
