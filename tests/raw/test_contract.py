from py4vasp.raw import _contract
from unittest.mock import patch


def return_generated_sources(example):
    return example.sources


@patch("py4vasp.raw._contract.run_example", side_effect=return_generated_sources)
def test_examples_cover_all_sources(mock_run):
    covered_sources = set()
    for example in _contract.EXAMPLES.values():
        covered_sources |= _contract.run_example(example)
