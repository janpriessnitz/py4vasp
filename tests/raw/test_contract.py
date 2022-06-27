from py4vasp.raw import _contract, _definition
from unittest.mock import patch
import pytest


def return_generated_sources(example):
    return example.sources


@pytest.mark.xfail(reason="not all examples are generated yet")
@patch("py4vasp.raw._contract.run_example", side_effect=return_generated_sources)
def test_examples_cover_all_sources(mock_run):
    expected_sources = set()
    for quantity, sources in _definition.schema.sources.items():
        expected_sources |= {(quantity, source) for source in sources}
    covered_sources = set()
    for example in _contract.EXAMPLES.values():
        covered_sources |= _contract.run_example(example)
    assert expected_sources == covered_sources
