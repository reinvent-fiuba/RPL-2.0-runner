import shutil
import subprocess
import sys

class RunnerError(Exception):
  def __init__(self, stage, message):
        super().__init__(message)
        self.stage = stage
        self.message = message

class Runner:
    
    BUILD_TIMEOUT = 20
    RUN_TIMEOUT = 60

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        '''
        Receives a path where all the files are and the test_type (I/O or unit)
        '''
        self.path = path
        self.test_type = test_type
        self.stage = "PREPARING"
        self.stdout = stdout
        self.stderr = stderr

    def exec_cmd(self, cmd, timeout):
        try:
            output, _ = cmd.communicate(timeout)
            
        except subprocess.TimeoutExpired:
            cmd.kill()
            msg = f"{self.stage} error\n  TIMEOUT {timeout}"
            output, _ = cmd.communicate()

        return output.decode("utf-8", "replace")

    def my_print(self, m):
        print(m, file=self.stdout)

    def log_divider(self, message, fill, align, width):
        self.my_print('{message:{fill}{align}{width}}'.format(
            message=message,
            fill=fill,
            align=align,
            width=width,
        ))

    def log(self, output):
        self.log_divider(f"{self.stage} OUTPUT:", ":", '^', 150)
        self.my_print(output)
        self.log_divider(f"END {self.stage} OUTPUT:", ":", '^', 150)

    def process(self):
        self.generate_files()
        self.build()
        return self.run()


    def build(self):
        self.stage = "BUILD"
        build_cmd = self.build_cmd()
        output = self.exec_cmd(build_cmd, self.BUILD_TIMEOUT)
        
        self.log(output)

        if build_cmd.returncode != 0:
            self.my_print(f"BUILD ERROR: error_code --> {build_cmd.returncode}")
            raise RunnerError(self.stage, f"Codigo Error {build_cmd.returncode}")


    def run(self):
        self.stage = "RUN"
        run_cmd = self.run_cmd()
        output = self.exec_cmd(run_cmd, self.RUN_TIMEOUT)
        
        self.log(output)

        if run_cmd.returncode == 0:
            self.my_print("RUN Todo OK")
        else:
            self.my_print("RUN ERROR")
            raise RunnerError(self.stage, f"Codigo Error {build_cmd.returncode}")

        return run_cmd.returncode

    def generate_files(self):
        pass

    def build_cmd(self):
        pass

    def run_cmd(self):
        raise NotImplementedError()


class CRunner(Runner):

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(path, test_type, stdout, stderr)


    def generate_files(self):
        shutil.copy("/Makefile", self.path)

    def build_cmd(self):
        return subprocess.Popen(["make", "-k", "main"], cwd=self.path, stdin=subprocess.DEVNULL, 
                stdout=subprocess.PIPE, stderr=self.stderr)

    def run_cmd(self):
        if self.test_type == "IO":
            with open(self.path + "/input.txt") as test_in:
                return subprocess.Popen([self.path + "/main"], cwd=self.path, stdin=test_in,
                        stdout=subprocess.PIPE, stderr=self.stderr)
        else:
            return subprocess.Popen([self.path + "/main"], cwd=self.path, stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE, stderr=self.stderr)














# def run():
#   # Copio nuestro Makefile a la carpeta donde estan los archivos
#             shutil.copy("/Makefile", tmpdir)


#             # Build
#             #cmd = subprocess.Popen(["gcc", "test_file.c", "-o", "output_c", "-Wall"], cwd=tmpdir, stdin=subprocess.DEVNULL,
#             #           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#             cmd = subprocess.Popen(["make", "-k", "main"], cwd=tmpdir, stdin=subprocess.DEVNULL,
#                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#             try:
#                 output, _ = cmd.communicate()
            
#             except subprocess.TimeoutExpired:
#                 cmd.kill()  # Will cleanup all children thanks to ProcessGroup above.
#                 msg = ("ERROR\n\n  TIMEOUTTT {}".format(timeout))
#                 output, _ = cmd.communicate()

#             self.my_print("\nCOMPILE:::::Todo OK" if cmd.returncode == 0 else msg,
#                   output.decode("utf-8", "replace"), sep="\n\n", end="")


#             print("RESULTADO DE COMPILE::::")
#             ls = subprocess.run(["ls", "-l"], cwd=tmpdir, capture_output=True, text=True)
#             print(ls.stdout)


#             # Run IO Test
#             with open(tmpdir + "/input.txt") as test_in:
#                 cmd = subprocess.Popen([tmpdir + "/main"], cwd=tmpdir, stdin=test_in,
#                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#                 try:
#                     output, _ = cmd.communicate()
                
#                 except subprocess.TimeoutExpired:
#                     cmd.kill()  # Will cleanup all children thanks to ProcessGroup above.
#                     msg = ("ERROR\n\n  TIMEOUTTT {}".format(timeout))
#                     output, _ = cmd.communicate()

#                 print("\n\nRUN::::::Todo OK" if cmd.returncode == 0 else msg,
#                       output.decode("utf-8", "replace"), sep="\n\n", end="")