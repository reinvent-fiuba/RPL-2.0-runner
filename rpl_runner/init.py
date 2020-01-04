import tempfile
import subprocess
import tarfile
import sys
import shutil
import json
import io

from custom_runner import CRunner, PythonRunner
from runner import RunnerError

custom_runners = {"c_std11": CRunner, "python_3.7": PythonRunner}


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--lang', help='Language of the assignment')

    return parser.parse_args()

def main():
    '''
    Punto de entrada del runner, el proceso corriendo dentro de un
    contenedor docker para correr los scripts de los alumnes
    '''
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
                runner = custom_runners[lang](tmpdir, "IO", my_stdout, my_stderr)

                result = {}
                try:
                    # Comenzamos la corrida
                    runner.process()
                    result["result"] = "OK"
                    result["stage"] = "COMPLETE"
                    result["message"] = "Completed all stages"
                except RunnerError as e:
                    result["result"] = "ERROR"
                    result["stage"] = e.stage
                    result["message"] = e.message

                    # print("HUBO ERRORES :))))))", e.message, "en la etapa:", e.stage)

                my_stdout.seek(0)
                my_stderr.seek(0)
                result["stdout"] = my_stdout.read()
                result["stderr"] = my_stderr.read()

                # Escribimos en el stdout del proceso por única vez
                print(json.dumps(result, indent=4)) # Contenido que recibe el proceso que ejecuta el contenedor docker

main()



# Funciones para probar

def pwd():
    pwd = subprocess.run(["pwd"], cwd=tmpdir, capture_output=True, text=True)
    print(pwd.stdout, file=sys.stderr)

def ls():
    ls = subprocess.run(["ls", "-l"], cwd=tmpdir, capture_output=True, text=True)
    print(ls.stdout, file=sys.stderr)