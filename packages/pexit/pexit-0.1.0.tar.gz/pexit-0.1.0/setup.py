import subprocess

from setuptools import setup
from setuptools.command.build_py import build_py


class CustomBuild(build_py):
    def run(self):
        print("Compiling C program...")
        subprocess.check_call(["gcc", "src/pexit/pexit.c", "-o", "src/pexit/pexit"])
        super().run()


setup(cmdclass={"build_py": CustomBuild})
