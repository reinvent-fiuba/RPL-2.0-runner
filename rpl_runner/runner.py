import shutil
import subprocess
import sys
import io
from pathlib import Path

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
        cmd_name, cmd_cmd = cmd
        self.logger.info(cmd_name)
        try:
            output, _ = cmd_cmd.communicate(timeout)
            
        except subprocess.TimeoutExpired:
            cmd_cmd.kill()
            msg = f"{self.stage} error\n  TIMEOUT {timeout}"
            output, _ = cmd_cmd.communicate()

        output = output.decode("utf-8", "replace").rstrip()
        self.log(output)
        
        return output

    def exec_cmds(self, cmds, timeout):
        '''Lo mismo que la de arriba pero muchos comandos'''
        results = []
        for cmd in cmds:
            results.append(self.exec_cmd(cmd, timeout))
        return results

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

        cmd_name, cmd_cmd = build_cmd
        if cmd_cmd.returncode != 0:
            self.my_print(f"BUILD ERROR: error_code --> {cmd_cmd.returncode}")
            raise RunnerError(self.stage, f"Error en {cmd_name}. Codigo Error {cmd_cmd.returncode}")

        self.logger.info("Build Ended")


    def run(self):
        self.logger.info("Run Started")

        self.stage = "RUN"
        run_cmds = self.run_cmd()
        outputs = self.exec_cmds(run_cmds, self.RUN_TIMEOUT)

        for cmd_name, cmd_cmd in run_cmds:
            if cmd_cmd.returncode != 0:
                self.logger.info("RUN ERROR")
                raise RunnerError(self.stage, f"Error en {cmd_name}. Codigo Error {cmd_cmd.returncode}")
        self.logger.info("RUN OK")
            

        self.logger.info("Run Ended")
        return 0

    def generate_files(self):
        raise NotImplementedError()


    def build_cmd(self):
        return ("Building", subprocess.Popen(["make", "-k", "build"], cwd=self.path, stdin=subprocess.DEVNULL, 
                stdout=subprocess.PIPE, stderr=self.stderr))

    def run_cmd(self):
        runs = []
        if self.test_type == "IO":
            cwd = Path(self.path)
            io_input_files = cwd.glob('IO_test_*')
            if not io_input_files:
                raise Exception("NO HAY INPUT FILES")
                return

            for input_file in sorted(io_input_files):                
                f = open(input_file.resolve().as_posix(), "r")  # We don't care about resourses of a disposable docker container
                runs.append((f"IO TEST: {input_file.name}", subprocess.Popen(["make", "-k", "run"], cwd=self.path, stdin=f,
                            stdout=subprocess.PIPE, stderr=self.stderr)))
        else:
            return [("Running Unit Tests", subprocess.Popen(["make", "-k", "run"], cwd=self.path, stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE, stderr=self.stderr))]
        return runs


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
