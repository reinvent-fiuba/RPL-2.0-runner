import sys
import subprocess
import shutil

from runner import Runner


class CRunner(Runner):

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(path, test_type, stdout, stderr)


    def generate_files(self):
        shutil.copy("/c_Makefile", self.path + "/Makefile")


class PythonRunner(Runner):

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(path, test_type, stdout, stderr)


    def generate_files(self):
        shutil.copy("/python_Makefile", self.path + "/Makefile")