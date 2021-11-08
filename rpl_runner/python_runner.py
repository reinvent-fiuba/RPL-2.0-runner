import shutil
import subprocess
import sys

from runner import Runner, RunnerError

class PythonRunner(Runner):
    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(path, test_type, stdout, stderr)

    def generate_files(self):
        shutil.copy("/python_Makefile", self.path + "/Makefile")
        if self.test_type != "IO":
            shutil.copy(
                "/usr/unit_test_wrapper.py", self.path + "/unit_test_wrapper.py"
            )
        else:
            shutil.copy(
                "/usr/custom_IO_main.py", self.path + "/custom_IO_main.py"
            )

    def build_cmd(self):
        """
        We are using (pyinstaller)[https://pyinstaller.readthedocs.io/en/stable/usage.html] 
        to generate a binary file and then executing it in the 
        """
        if self.test_type == "IO":
            build_command = "build_io"
        else:
            build_command = "build_unit_test"

        return (
            "Building",
            subprocess.Popen(
                ["make", "-k", build_command],
                cwd=self.path,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=self.stderr,
                start_new_session=True,
            ),
        )

