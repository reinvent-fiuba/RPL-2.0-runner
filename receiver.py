import tempfile
import subprocess
import tarfile
import time
import json
import sys
import requests

def main():
  ejecutar(1, sys.argv[1] if len(sys.argv) > 1 else 'c')


def ejecutar(submission_id, lang='c'):
  """Función principal del script.
  """
  with tempfile.TemporaryDirectory(prefix="corrector.") as tmpdir:
    
    solution_tar = "tar_assignment_solved_c.tar.gz"  # Obtener a partir del id del mensaje
    #Cuando salgo de aca se deberia eliminar todo lo relacionado con esta entrega ya que vive en este directorio temporal

    response = requests.get(f"http://localhost:8080/api/submissions/{submission_id}")

    print(json.dumps(response.json(), indent=4))
    
    if response.status_code != 200:
      raise Exception("Error al obtener la Submission")

    submission = response.json()

    file_id = submission['file_id']
    file_name = submission['file_name']
    activity_language = submission['activity_language']


    file_response = requests.get(f"http://localhost:8080/api/files/{file_id}")

    if file_response.status_code != 200:
      raise Exception("Error al obtener el comprimido")


    with open('PROBANDO_' + file_name, 'wb') as f:
        f.write(file_response.content)


    print(f"Obteniendo submission {submission_id}....")
    time.sleep(1) #ahre
    print(f"Submission obtenida: {solution_tar}")

    print("Ejecutando codigo en contenedor docker")
    # Lanzar ya el proceso worker para poder pasar su stdin a tarfile.open().
    # --rm --> clean up container after run
    #
    with subprocess.Popen(["docker", "run", "--rm", "--interactive", "--env", "LANG=C.UTF-8", "rpl-2.0-runner", "--lang", lang],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT) as worker:

      print(type(file_response.content))
      worker.stdin.write(file_response.content)


      # tar = tarfile.open(fileobj=worker.stdin, mode="w|", dereference=True)
      # tar.add("input.txt")
      # tar.add("output.txt")
      # tar.add("test_file.c")
      # tar.add("main.py")

      # tar.close()


      stdout, _ = worker.communicate()
      json_output = stdout.decode("utf-8", "replace")
      retcode = worker.wait()

      print("Resultado:\n\n")

      print(json_output)

      result = json.loads(json_output)

      # print(result)

      print("################## STDOUT ######################")
      print(result["stdout"])
      print("################## STDOUT ######################")
      print("################## STDERR ######################")
      print(result["stderr"])
      print("################## STDERR ######################")

      print(f"Código de retorno de ejecución: {retcode}")

      # mandar resultado (json_output/result) POST al backend


    # except Timeout:
      # raise Error("TIMEOUT")


if __name__ == "__main__":
  main()