from unittest.mock import patch
from py4vasp.control import POSCAR
import py4vasp.data as data
from .test_base import AbstractTest


class TestPoscar(AbstractTest):
    tested_class = POSCAR


def test_plot_poscar():
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
    cm_init = patch.object(data.Viewer3d, "__init__", autospec=True, return_value=None)
    cm_cell = patch.object(data.Viewer3d, "show_cell")
    with cm_init as init, cm_cell as cell:
        poscar.plot()
        init.assert_called_once()
        cell.assert_called_once()


def test_plot_argument_forwarding():
    text = "! comment line"
    poscar = POSCAR.from_string(text)
    with patch.object(data.Structure, "from_POSCAR") as struct:
        poscar.plot("argument", key="value")
        struct.return_value.plot.assert_called_once_with("argument", key="value")