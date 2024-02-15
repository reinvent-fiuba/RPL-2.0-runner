import json
import subprocess
import sys
import tarfile
import tempfile
import os

from python_runner import PythonRunner
from c_runner import CRunner
from go_runner import GoRunner
from runner import RunnerError, TimeOutError
from logger import get_logger

LOG = get_logger("RPL-2.0-worker-init")

custom_runners = {
    "c_std11": CRunner,
    "python_3.7": PythonRunner,
    "go_1.16": GoRunner, # Just to have support for test submissions
    "go_1.19": GoRunner
}


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(prog="RPL Submission Runner")
    parser.add_argument("--lang", help="Language of the assignment")
    parser.add_argument(
        "--test-mode", help='Type of test ("IO" or "unit_test")', dest="mode"
    )

    return parser.parse_args()


def main():
    """
    Punto de entrada del runner, el proceso corriendo dentro de un
    contenedor docker para correr los scripts de los alumnes
    """
    args = parse_args()
    lang = args.lang
    test_mode = args.mode

    # Usamos sys.stdin.buffer para leer en binario (sys.stdin es texto).
    # Asimismo, el modo ‘r|’ (en lugar de ‘r’) indica que fileobj no es
    # seekable.

    # Todavia no descubro como evitar tener que escribir y luego leer...
    # Por ahora es un buen workarround
    with open("assignment.tar.gx", "wb") as assignment:
        assignment.write(sys.stdin.buffer.read())

    process(lang, test_mode, "assignment.tar.gx")


def process(lang, test_mode, filename, cflags=""):
    os.environ["CFLAGS"] = cflags
    if "-l" in cflags:
        os.environ["CFLAGS"] = " ".join([x if "-l" not in x else "" for x in cflags.split()])
        os.environ["LDFLAGS"] = " ".join([x if "-l" in x else "" for x in cflags.split()])

    with tempfile.TemporaryDirectory(prefix="corrector.") as tmpdir:
        LOG.info(f"Extracting tarfile submission from {filename}")
        with tarfile.open(filename) as tar:
            tar.extractall(tmpdir)

        # Escribimos los logs, stdout y stderr en archivos temporarios para despues poder devolverlo
        # y que el usuario vea que paso en su corrida
        with tempfile.TemporaryFile(
            dir=tmpdir, prefix="stdout.", mode="w+", encoding="utf-8"
        ) as my_stdout, tempfile.TemporaryFile(
            dir=tmpdir, prefix="stderr.", mode="w+", encoding="utf-8"
        ) as my_stderr:
            # Obtenemos el runner del lenguaje y modo seleccionado
            LOG.info("Running custom runner")
            test_runner = custom_runners[lang](tmpdir, test_mode, my_stdout, my_stderr)
            LOG.info("Custom runner ran succesfully")
            result = {}
            try:
                # Comenzamos la corrida
                test_runner.process()  # writes stuff to my_stdout and my_stderr
                result["test_run_result"] = "OK"
                result["test_run_stage"] = "COMPLETE"
                result["test_run_exit_message"] = "Completed all stages"
            except TimeOutError as e:
                result["test_run_result"] = "TIME_OUT"
                result["test_run_stage"] = e.stage
                result["test_run_exit_message"] = e.message
            except RunnerError as e:
                result["test_run_result"] = "ERROR"
                result["test_run_stage"] = e.stage
                result["test_run_exit_message"] = e.message
                LOG.error("HUBO ERRORES: {message} en la etapa de {stage}".format(message=e.message, stage=e.stage))
            except Exception as e:
                result["test_run_result"] = "UNKNOWN_ERROR"
                result["test_run_stage"] = "unknown"
                result["test_run_exit_message"] = str(e)
                raise e
            # Get criterion unit tests results
            if test_mode == "unit_test" and result["test_run_stage"] == "COMPLETE":
                result["test_run_unit_test_result"] = get_unit_test_results(
                    tmpdir, lang
                )
            else:
                result["test_run_unit_test_result"] = None  # Nice To have for debbuging
            my_stdout.seek(0)
            my_stderr.seek(0)
            result["test_run_stdout"] = my_stdout.read(9999)  # we can only store up to 10k chars in the column
            result["test_run_stderr"] = my_stderr.read(9999)
            result["stdout_only_run"] = parse_stdout(result["test_run_stdout"])
            LOG.info(json.dumps(result, indent=4))
            return result


def parse_stdout(log_stdout):
    """
    Devuelve una lista de todas las salidas de las corridas SIN EL LOGGING.
    Se identifica como salida del programa a todo el stdout entre el log start_RUN y end_RUN
    """
    results = []
    result = ""
    for line in log_stdout.split("\n"):
        if "end_RUN" in line:
            results.append(result)

        elif "start_RUN" in line:
            result = ""

        elif (
            "custom_IO_main.pyc" in line
            or "assignment_main.py" in line
            or "./main" in line
        ):
            continue

        else:
            result += line + "\n"

    return results


def get_unit_test_results(tmpdir, lang):
    cat = subprocess.run(
        ["cat", "unit_test_results_output.json"],
        cwd=tmpdir,
        capture_output=True,
        text=True,
        errors="ignore",
    )
    if not cat.stdout:
        return None

    try:
        output = "".join(
            c for c in cat.stdout if ord(c) >= 32
        )  # sanitizing string as criterion output can add weird characters
        if lang == "c_std11":
            return get_custom_unit_test_results_json(output)
        return json.loads(output)
    except json.decoder.JSONDecodeError as e:
        LOG.exception(str(output).replace("\x03", ""))
        return None


# Check out util_files/salida_criterion.json to see raw format
def get_custom_unit_test_results_json(criterion_json):
    parsed_json = json.loads(str(criterion_json))
    result = {}
    if parsed_json["test_suites"] and len(parsed_json["test_suites"]) > 0:
        result["passed"] = parsed_json["passed"]
        result["failed"] = parsed_json["failed"]
        result["errored"] = parsed_json["errored"]
        result["tests"] = parsed_json["test_suites"][0]["tests"]

    for i in range(len(result["tests"])):
        if result["tests"][i]["status"] in ["FAILED", "ERRORED"]:
            result["tests"][i]["messages"] = ";    ".join(
                result["tests"][i]["messages"]
            )
    return result


# Funciones para probar


def pwd(dir):
    pwd = subprocess.run(["pwd"], cwd=dir, capture_output=True, text=True)
    print(pwd.stdout, file=sys.stderr)


def ls(dir):
    ls = subprocess.run(["ls", "-l"], cwd=dir, capture_output=True, text=True)
    print(ls.stdout, file=sys.stderr)


# main()
