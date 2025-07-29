import os
import sys


def main():
    path = os.path.join(os.path.dirname(__file__), "pexit")
    assert os.path.exists(path), f"Cannot find `pexit` executable in {path}"
    os.execvp(path, ["pexit"] + sys.argv[1:])
