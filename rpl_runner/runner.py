import os
import signal
import subprocess
import sys
from pathlib import Path


class RunnerError(Exception):
    def __init__(self, stage, message):
        super().__init__(message)
        self.stage = stage
        self.message = message

class TimeOutError(RunnerError):
    def __init__(self, stage, message):
        super().__init__(stage, message)

class Runner:
    """
    Base clase with the necessary steps to prepare, build and run an assignment
    either with unit tests or IO tests.
    """

    BUILD_TIMEOUT = 20
    RUN_TIMEOUT = 10

    def __init__(self, path, test_type, stdout=sys.stdout, stderr=sys.stderr):
        """
        Receives a path where all the files are and the test_type (I/O or unit)
        """
        self.path = path
        self.test_type = test_type
        self.stage = "PREPARING"
        self.stdout = stdout
        self.stderr = stderr
        self.logger = get_logger(stdout)

    def process(self):
        """
        Only public function. Does all the work.
        - generate_files must be implemented by a custom runner extending this class.
        - Build depends onthe custom runner's generated Makefile and executes 'make -k build'
        - Run command just executes 'make -k run' and pipes the input files in case it IO tested
        """
        self.generate_files()
        self.build()
        return self.run()

    def exec_cmd(self, cmd, timeout):
        """
        Executes a single command and logs the output.
        Receives the command name (just for logging) and the actual subprocess.Popen instance
        Everything between 'start_*' and 'end_*' is what the student will see as output.
        """
        cmd_name, cmd_cmd = cmd
        self.logger.info(cmd_name)
        self.logger.info(f"start_{self.stage}")
        output = ""
        try:
            output, _ = cmd_cmd.communicate(timeout=timeout)

            output = output.decode("utf-8", "replace").rstrip()            
            self.log(output)            
            self.logger.info(f"end_{self.stage}")

            return output

        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(cmd_cmd.pid), signal.SIGKILL)  # Send the signal to all the process groups
            os.killpg(os.getpgid(cmd_cmd.pid + 1), signal.SIGKILL)  # For some reason it happens that we are not sending SIGKILL to the main process executed by Makefile. This makes sure we send SIGKILL to that process, and not to the Makefile process
            cmd_cmd.kill()
            output, error = cmd_cmd.communicate()
            self.log("TIMEOUT")
            if error: self.log(error)
            if output: self.log(output)
            return "TIMEOUT"

        
    def exec_cmds(self, cmds, timeout):
        """Lo mismo que la de arriba pero muchos comandos"""
        results = []
        for cmd in cmds:
            results.append(self.exec_cmd(cmd, timeout))
        return results

    def build(self):
        """
        Build process.
        If build fails raises RunnerError.
        Heavily depends on the generated Makefile in the generate_files step.
        """
        self.stage = "BUILD"
        self.logger.info("Build Started")
        build_cmd = self.build_cmd()
        output = self.exec_cmd(build_cmd, self.BUILD_TIMEOUT)

        cmd_name, cmd_cmd = build_cmd
        if cmd_cmd.returncode == -9:  # TIMEOUT
            self.my_print(f"BUILD ERROR: error_code --> {cmd_cmd.returncode}")
            raise TimeOutError(self.stage,f"Error en {cmd_name}. TIMEOUT")
        if cmd_cmd.returncode != 0:
            self.my_print(f"BUILD ERROR: error_code --> {cmd_cmd.returncode}")
            raise RunnerError(
                self.stage, f"Error en {cmd_name}. Codigo Error {cmd_cmd.returncode}"
            )

        self.logger.info("Build Ended")

    def run(self):
        """
        Run process.
        If returncode is not 0, raises RunnerError.
        Heavily depends on the generated Makefile in the generate_files step.
        """
        self.logger.info("Run Started")

        self.stage = "RUN"
        run_cmds = self.run_cmd()
        outputs = self.exec_cmds(run_cmds, self.RUN_TIMEOUT)

        for cmd_name, cmd_cmd in run_cmds:
            if cmd_cmd.returncode == -9: # TIMEOUT
                raise TimeOutError(self.stage,f"Error en {cmd_name}. TIMEOUT")

            if cmd_cmd.returncode != 0:
                self.logger.info("RUN ERROR")
                raise RunnerError(
                    self.stage,
                    f"Error en {cmd_name}. Codigo Error {cmd_cmd.returncode}",
                )
        self.logger.info("RUN OK")

        self.logger.info("Run Ended")
        return 0

    def generate_files(self):
        """
        Step aimed to prepare the environment for the assignment to be successfuly run, this includes:
            - Adding a custom Makefile  <----- IMPORTANT ----->
            - Any extra files the activity needs
        """
        raise NotImplementedError()

    def build_cmd(self):
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
        
    def run_cmd(self):
        """
        Returns a list of tuples with the structure (<process_name>, <subprocess.Popen instante>)
        If it's an IO test, there will probably be multiple test scenarios therefore many runs.
        """
        runs = []
        if self.test_type == "IO":
            cwd = Path(self.path)
            io_input_files = list(cwd.glob("IO_test_*"))

            if len(io_input_files) == 0:
                return [
                    (
                        f"SIN UNIT TEST",
                        subprocess.Popen(
                            ["make", "-k", "run"],
                            cwd=self.path,
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE,
                            stderr=self.stderr,
                            start_new_session=True,
                        ),
                    )
                ]

            for input_file in sorted(io_input_files):
                f = open(
                    input_file.resolve().as_posix(), "r"
                )  # We don't care about resourses of a disposable docker container
                runs.append(
                    (
                        f"IO TEST: {input_file.name}",
                        subprocess.Popen(
                            ["make", "-k", "run"],
                            cwd=self.path,
                            stdin=f,
                            stdout=subprocess.PIPE,
                            stderr=self.stderr,
                            start_new_session=True,
                        ),
                    )
                )
        else:
            return [
                (
                    "Running Unit Tests",
                    subprocess.Popen(
                        ["make", "-k", "run_unit_test"],
                        cwd=self.path,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,
                        stderr=self.stderr,
                        start_new_session=True,
                    ),
                )
            ]
        return runs

    def my_print(self, m):
        print(m, file=self.stdout)

    def log_divider(self, message, fill, align, width):
        self.my_print(
            "{message:{fill}{align}{width}}".format(
                message=message, fill=fill, align=align, width=width,
            )
        )

    def log(self, output):
        # self.log_divider(f"{self.stage} OUTPUT:", ":", '^', 150)
        self.my_print(output)
        # self.log_divider(f"END {self.stage} OUTPUT:", ":", '^', 150)


def get_logger(stdout):
    import logging

    logger = logging.getLogger("RPL-2.0")
    handler = logging.StreamHandler(stdout)
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
