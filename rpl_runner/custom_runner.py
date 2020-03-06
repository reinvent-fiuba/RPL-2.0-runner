import sys
import subprocess
import shutil

from runner import Runner


class CRunner(Runner):

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(path, test_type, stdout, stderr)


    def generate_files(self):
        shutil.copy("/c_Makefile", self.path + "/Makefile")

    def build_cmd(self):
        if self.test_type == "IO":
            return ("Building", subprocess.Popen(["make", "-k", "build"], cwd=self.path, stdin=subprocess.DEVNULL, 
                stdout=subprocess.PIPE, stderr=self.stderr))
        else:
            return ("Building", subprocess.Popen(["gcc", "unit_test.c", "-o", "main", "-lcriterion", "-Wall", "-lm"], cwd=self.path, stdin=subprocess.DEVNULL, 
                stdout=subprocess.PIPE, stderr=self.stderr))


class PythonRunner(Runner):

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(path, test_type, stdout, stderr)


    def generate_files(self):
        shutil.copy("/python_Makefile", self.path + "/Makefile")