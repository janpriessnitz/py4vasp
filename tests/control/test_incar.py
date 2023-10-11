# Copyright © VASP Software GmbH,
# Licensed under the Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
import pytest

from py4vasp.control import INCAR
from py4vasp._control.incar import parse_incar_to_dict

from .test_base import AbstractTest


class TestIncar(AbstractTest):
    tested_class = INCAR


@pytest.mark.parametrize(
    "input, output",
    [
        ("# empty file", {}),
        ("tag1 = value1 \n tag2 = value2", {"TAG1": "value1", "TAG2": "value2"}),
    ],
)
def test_from_string(input, output):
    assert parse_incar_to_dict(input) == output
