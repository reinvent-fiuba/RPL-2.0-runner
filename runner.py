import tempfile
import subprocess
import tarfile
import sys
import shutil
import json

from runner_c import CRunner, RunnerError

def main():
    with tempfile.TemporaryDirectory(prefix="corrector.") as tmpdir:
    # Usamos sys.stdin.buffer para leer en binario (sys.stdin es texto).
    # Asimismo, el modo ‘r|’ (en lugar de ‘r’) indica que fileobj no es
    # seekable.
        with tarfile.open(fileobj=sys.stdin.buffer, mode="r|") as tar:
            tar.extractall(tmpdir)

            with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as my_stdout, \
                    tempfile.TemporaryFile(mode="w+", encoding="utf-8") as my_stderr:

                runner = CRunner(tmpdir, "IO", my_stdout, my_stderr)

                result = {}
                try:
                    runner.process()
                    result["result"] = f"OK"
                    result["stage"] = "COMPLETE"
                    result["message"] = "Completed all stages"
                except RunnerError as e:
                    result["result"] = f"ERROR"
                    result["stage"] = e.stage
                    result["message"] = e.message

                    # print("HUBO ERRORES :))))))", e.message, "en la etapa:", e.stage)

                my_stdout.seek(0)
                my_stderr.seek(0)
                result["stdout"] = my_stdout.read()
                result["stderr"] = my_stderr.read()

                print(json.dumps(result, indent=4))





            # pwd = subprocess.run(["pwd"], cwd=tmpdir, capture_output=True, text=True)
            # # print(pwd.stdout, file=sys.stderr)


            # ls = subprocess.run(["ls", "-l"], cwd=tmpdir, capture_output=True, text=True)
            # # print(ls.stdout, file=sys.stderr)


            # # Copio nuestro Makefile a la carpeta donde estan los archivos
            # shutil.copy("/Makefile", tmpdir)
main()