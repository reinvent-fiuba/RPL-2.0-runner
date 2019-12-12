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
        self.logger = get_logger(stdout)

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
        # self.log_divider(f"{self.stage} OUTPUT:", ":", '^', 150)
        self.my_print(output)
        # self.log_divider(f"END {self.stage} OUTPUT:", ":", '^', 150)

    def process(self):
        self.generate_files()
        self.build()
        return self.run()


    def build(self):
        self.stage = "BUILD"
        self.logger.info("Build Started")
        build_cmd = self.build_cmd()
        output = self.exec_cmd(build_cmd, self.BUILD_TIMEOUT)
        
        self.log(output)

        if build_cmd.returncode != 0:
            self.my_print(f"BUILD ERROR: error_code --> {build_cmd.returncode}")
            raise RunnerError(self.stage, f"Codigo Error {build_cmd.returncode}")

        self.logger.info("Build Ended")


    def run(self):
        self.logger.info("Run Started")

        self.stage = "RUN"
        run_cmd = self.run_cmd()
        output = self.exec_cmd(run_cmd, self.RUN_TIMEOUT)
        
        self.log(output)

        if run_cmd.returncode == 0:
            self.logger.info("RUN Todo OK")
        else:
            self.logger.info("RUN ERROR")
            raise RunnerError(self.stage, f"Codigo Error {run_cmd.returncode}")

        self.logger.info("Run Ended")
        return run_cmd.returncode

    def generate_files(self):
        raise NotImplementedError()


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


def get_logger(stdout):
    import logging

    logger = logging.getLogger('RPL-2.0')
    handler = logging.StreamHandler(stdout)
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
