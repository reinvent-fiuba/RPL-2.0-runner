import json
import subprocess
import sys
import tarfile
import tempfile

from custom_runner import CRunner, PythonRunner
from runner import RunnerError

custom_runners = {"c_std11": CRunner, "python_3.7": PythonRunner}


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--lang', help='Language of the assignment')

    return parser.parse_args()


def main():
    """
    Punto de entrada del runner, el proceso corriendo dentro de un
    contenedor docker para correr los scripts de los alumnes
    """
    args = parse_args()
    lang = args.lang

    with tempfile.TemporaryDirectory(prefix="corrector.") as tmpdir:
        # Usamos sys.stdin.buffer para leer en binario (sys.stdin es texto).
        # Asimismo, el modo ‘r|’ (en lugar de ‘r’) indica que fileobj no es
        # seekable.

        # Todavia no descubro como evitar tener que escribir y luego leer...
        # Por ahora es un buen workarround
        with open("assignment.tar.gx", "wb") as assignment:
            assignment.write(sys.stdin.buffer.read())

        with tarfile.open("assignment.tar.gx") as tar:
            tar.extractall(tmpdir)

            # Escribimos los logs, stdout y stderr en archivos temporarios para despues poder devolverlo
            # y que el usuario vea que paso en su corrida
            with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as my_stdout, \
                    tempfile.TemporaryFile(mode="w+", encoding="utf-8") as my_stderr:

                # Obtenemos el runner del lenguaje seleccionado
                # io_runner = custom_runners[lang](tmpdir, "IO", my_stdout, my_stderr)

                ls = subprocess.run(["ls", "-l"], cwd=tmpdir, capture_output=True, text=True)
                ls_output = ls.stdout
                if "unit_test" in ls_output:
                    mode = "unit_test"
                else:
                    mode = "IO"

                unit_test_runner = custom_runners[lang](tmpdir, mode, my_stdout, my_stderr)

                result = {}
                try:
                    # Comenzamos la corrida
                    # io_runner.process()
                    unit_test_runner.process()  # writes stuff to my_stdout and my_stderr
                    result["test_run_result"] = "OK"
                    result["test_run_stage"] = "COMPLETE"
                    result["test_run_exit_message"] = "Completed all stages"
                except RunnerError as e:
                    result["test_run_result"] = "ERROR"
                    result["test_run_stage"] = e.stage
                    result["test_run_exit_message"] = e.message

                    # print("HUBO ERRORES :))))))", e.message, "en la etapa:", e.stage)

                my_stdout.seek(0)
                my_stderr.seek(0)
                result["test_run_stdout"] = my_stdout.read()
                result["test_run_stderr"] = my_stderr.read()
                result["stdout_only_run"] = parse_stdout(result["test_run_stdout"])

                # Escribimos en el stdout del proceso por única vez
                print(json.dumps(result, indent=4))  # Contenido que recibe el proceso que ejecuta el contenedor docker


def parse_stdout(log_stdout):
    """
    Devuelve una lista de todas las salidas de las corridas SIN EL LOGGING.
    Se identifica como salida del programa a todo el stdout entre el log start_RUN y end_RUN
    """
    results = []
    result = ""
    for line in log_stdout.split('\n'):
        if "end_RUN" in line:
            results.append(result)

        elif "start_RUN" in line:
            result = ""

        elif "assignment_main.py" in line or "./main" in line:
            continue

        else:
            result += line

    return results


# Funciones para probar

def pwd(dir):
    pwd = subprocess.run(["pwd"], cwd=dir, capture_output=True, text=True)
    print(pwd.stdout, file=sys.stderr)


def ls(dir):
    ls = subprocess.run(["ls", "-l"], cwd=dir, capture_output=True, text=True)
    print(ls.stdout, file=sys.stderr)


main()
