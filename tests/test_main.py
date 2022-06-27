from unittest.mock import patch
from hypothesis import given, strategies as strategy
from py4vasp.__main__ import main

alphabet = strategy.characters(whitelist_categories=("L", "N"))
command_argument = strategy.text(alphabet, min_size=1)


@patch("py4vasp.raw._contract.example")
@given(strategy.lists(command_argument, min_size=1))
def test_example(mock_example, args):
    main(["--example", *args])
    mock_example.assert_called_once_with(args)
    mock_example.reset_mock()
