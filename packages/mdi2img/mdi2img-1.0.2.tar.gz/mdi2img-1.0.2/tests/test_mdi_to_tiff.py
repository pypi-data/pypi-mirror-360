# tests/test_ask_question.py

"""
File in charge of testing the functions contained in the class
"""

from sys import stderr
import mdi2img


def print_debug(string: str = "") -> None:
    """ Print debug messages """
    debug = False
    if debug is True:
        print(f"DEBUG: {string}", file=stderr)


def test_this_is_not_a_test() -> None:
    """ Test the this is not a test function """
    print("Testing this is not a test")
    assert 0 == 0


def test_class_content() -> None:
    """ Test the class content """
    print("Testing class content")
    print(f"Displaying the content of mdi2img:\n{dir(mdi2img)}")
    assert 0 == 0
