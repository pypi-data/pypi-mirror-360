#!/usr/bin/env python3
from pyfromroot.version import __version__
from fire import Fire

# print("v... unit 'unitname' loaded, version:",__version__)

def func(debug = False):

    print("D... in unit unitname function func DEBUG may be filtered")
    print("i... in unit unitname function func - info")
    print("X... in unit unitname function func - ALERT")
    return True

def test_func():
    print("i... TESTING function func")
    assert func() == True

if __name__ == "__main__":
    print("i... in the __main__ of unitname of pyfromroot")
    Fire()

    