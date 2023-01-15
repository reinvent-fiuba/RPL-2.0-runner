import shutil
import subprocess
import sys
from os import listdir

from runner import Runner, RunnerError


class GoRunner(Runner):
    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        print("GoRunner")
        super().__init__(path, test_type, stdout, stderr)

    def generate_files(self):
        shutil.copy("/go_Makefile", self.path + "/Makefile")
        print(listdir("/"))
        shutil.copy("/go.mod", self.path)
        shutil.copy("/go.sum", self.path)
        shutil.copy("/go_parser.py", self.path)

    def build_cmd(self):
        if self.test_type == "IO":
            return (
                "Building",
                subprocess.Popen(
                    ["make", "-k", "build"],
                    cwd=self.path,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=self.stderr,
                    start_new_session=True,
                ),
            )
        else:
            # First we check that the student files compile,
            # otherwise the error message will be mixed with criterion files
            build_only_sudent_files = subprocess.Popen(
                ["make", "-k", "build_pre_unit_test"],
                cwd=self.path,
                stdin=subprocess.DEVNULL,
                stdout=self.stdout,
                stderr=self.stderr,
            )

            output, _ = build_only_sudent_files.communicate()

            if build_only_sudent_files.returncode != 0:
                self.my_print(
                    f"BUILD ERROR: error_code --> {build_only_sudent_files.returncode}"
                )
                raise RunnerError(
                    self.stage,
                    f"Error de compilación. Codigo Error {build_only_sudent_files.returncode}",
                )

            return (
                "Building",
                subprocess.Popen(
                    ["make", "-k", "build_unit_test"],
                    cwd=self.path,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=self.stderr,
                    start_new_session=True,
                ),
            )
