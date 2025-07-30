# tests/test_ask_question.py

"""
File in charge of testing the functions contained in the class
"""

from sys import stderr
from window_asset_tkinter import WindowAsset


def print_debug(string: str = "") -> None:
    """ Print debug messages """
    debug = False
    if debug is True:
        print(f"DEBUG: {string}", file=stderr)


def test_no_test_can_be_run_for_graphical_environements():
    """ No tests can be run when in a graphical environement """
    assert 0==0
