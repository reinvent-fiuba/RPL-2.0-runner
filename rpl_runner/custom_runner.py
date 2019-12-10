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
        return subprocess.Popen(["make", "-k", "main"], cwd=self.path, stdin=subprocess.DEVNULL, 
                stdout=subprocess.PIPE, stderr=self.stderr)

    def run_cmd(self):
        if self.test_type == "IO":
            with open(self.path + "/input.txt") as test_in:
                return subprocess.Popen(["make", "-k", "run"], cwd=self.path, stdin=test_in,
                        stdout=subprocess.PIPE, stderr=self.stderr)
        else:
            return subprocess.Popen(["make", "-k", "run"], cwd=self.path, stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE, stderr=self.stderr)


class PythonRunner(Runner):

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(path, test_type, stdout, stderr)


    def generate_files(self):
        shutil.copy("/python_Makefile", self.path + "/Makefile")
        #O forzamos a que haya un "main.py" o tratamos de generarlo acá

    def build_cmd(self):
        return subprocess.Popen(["make", "-k", "build"], cwd=self.path, stdin=subprocess.DEVNULL, 
                stdout=subprocess.PIPE, stderr=self.stderr)

    def run_cmd(self):
        if self.test_type == "IO":
            with open(self.path + "/input.txt") as test_in:
                return subprocess.Popen(["make", "-k", "run"], cwd=self.path, stdin=test_in,
                        stdout=subprocess.PIPE, stderr=self.stderr)
        else:
            return subprocess.Popen(["make", "-k", "run"], cwd=self.path, stdin=test_in,
                        stdout=subprocess.PIPE, stderr=self.stderr)