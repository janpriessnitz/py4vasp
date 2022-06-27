import dataclasses
from py4vasp import exceptions as exception


@dataclasses.dataclass
class Example:
    sources: set
    POSCAR: str
    POTCAR: list
    INCAR: str = ""
    KPOINTS: str = None


def run_example(example):
    raise exception.NotImplemented


EXAMPLES = {
    "py4vasp_default_vasp_run": Example(
        sources={
            ("band", "default"),
            ("cell", "default"),
            ("dos", "default"),
            ("energies", "default"),
            ("forces", "default"),
            ("kpoint", "default"),
            ("structure", "default"),
            ("stress", "default"),
            ("topology", "default"),
        },
        POSCAR="""Sr2TiO4
 1.0
 6.922900  0.0       0.0
 4.694503  5.088043  0.0
-5.808696 -2.544019  2.777329
Sr Ti O
 2  1 4
Direct
0.64529 0.64529 0.0
0.35471 0.35471 0.0
0.0     0.0     0.0
0.84178 0.84178 0.0
0.15823 0.15823 0.0
0.5     0.0     0.5
0.0     0.5     0.5""",
        POTCAR=["Sr_sv", "Ti_sv", "O"],
    )
}
