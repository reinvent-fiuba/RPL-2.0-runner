import shutil
import subprocess
import sys

from runner import Runner, RunnerError


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
            # First we check that the student files compile,
            # otherwise the error message will be mixed with criterion files
            build_only_sudent_files = subprocess.Popen(["make", "-k", "build_pre_unit_test"],
                                                       cwd=self.path,
                                                       stdin=subprocess.DEVNULL,
                                                       stdout=self.stdout,
                                                       stderr=self.stderr)

            output, _ = build_only_sudent_files.communicate()

            if build_only_sudent_files.returncode != 0:
                self.my_print(f"BUILD ERROR: error_code --> {build_only_sudent_files.returncode}")
                raise RunnerError(self.stage,
                                  f"Error de compilación. Codigo Error {build_only_sudent_files.returncode}")

            return ("Building",
                    subprocess.Popen(["make", "-k", "build_unit_test"],
                                     cwd=self.path,
                                     stdin=subprocess.DEVNULL,
                                     stdout=subprocess.PIPE,
                                     stderr=self.stderr))
            # TODO: Luego de compilar, borrar todos los ".c" para que no hagan print de las pruebas


class PythonRunner(Runner):

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(path, test_type, stdout, stderr)

    def generate_files(self):
        shutil.copy("/python_Makefile", self.path + "/Makefile")
        if self.test_type != "IO":
            shutil.copy("/usr/unit_test_wrapper.py", self.path + "/unit_test_wrapper.py")
