# Copyright © VASP Software GmbH,
# Licensed under the Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
import pytest

from py4vasp import calculation
from py4vasp.control import POSCAR

from .test_base import AbstractTest


class TestPoscar(AbstractTest):
    tested_class = POSCAR


@pytest.mark.parametrize("supercell", [None, 2, (3, 2, 1)])
def test_plot_poscar(supercell, Assert):
    text = """! comment line
    5.43
    0.0 0.5 0.5
    0.5 0.0 0.5
    0.5 0.5 0.0
    Si
    2
    Direct
    0.00 0.00 0.00
    0.25 0.25 0.25
    """
    poscar = POSCAR.from_string(text)
    structure = calculation.structure.from_POSCAR(text)
    structure_view = structure.plot(supercell)
    view = poscar.plot(supercell) if supercell else poscar.plot()
    Assert.same_structure_view(view, structure_view)
    view = poscar.to_view(supercell) if supercell else poscar.to_view()
    Assert.same_structure_view(view, structure_view)
