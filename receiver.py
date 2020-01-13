import tempfile
import subprocess
import tarfile
import time
import json
import sys
import requests
import io

def main():
  ejecutar(int(sys.argv[1]) if len(sys.argv) > 1 else 1, sys.argv[2] if len(sys.argv) > 2 else 'c_std11')


def ejecutar(submission_id, lang='c_std11'):
  """
  Función principal del script.

  """
  with tempfile.TemporaryDirectory(prefix="corrector.") as tmpdir:
    
    solution_tar = "tar_assignment_solved_c.tar.gz"  # Obtener a partir del id del mensaje
    #Cuando salgo de aca se deberia eliminar todo lo relacionado con esta entrega ya que vive en este directorio temporal

    print(f"Obteniendo submission data {submission_id}....")
    #GET SUBMISSION
    response = requests.get(f"http://localhost:8080/api/submissions/{submission_id}")

    print(json.dumps(response.json(), indent=4))
    
    if response.status_code != 200:
      raise Exception("Error al obtener la Submission")

    submission = response.json()

    ## SUBMISSION AND ACTIVITY DETAILS

    submission_file_id = submission['submission_file_id']
    submission_file_name = submission['submission_file_id']

    activity_supporting_file_id = submission['activity_supporting_file_id']
    activity_supporting_file_name = submission['activity_supporting_file_name']
    
    activity_unit_tests = submission['activity_unit_tests'] # string with unit_test content
    activity_io_tests = submission['activity_iotests']  # Array of strings (input part of IO tests)
    
    activity_language = submission['activity_language']

    # ---------------------------------------------------------

    print(f"Obteniendo submission files {submission_file_id}....")
    #GET SUBMISSION FILES
    submission_file_response = requests.get(f"http://localhost:8080/api/files/{submission_file_id}")

    if submission_file_response.status_code != 200:
      raise Exception("Error al obtener el comprimido de submission")

    with open(tmpdir + '/submission_files.tar.gz', 'wb') as sf:
        sf.write(submission_file_response.content)

    # ---------------------------------------------------------

    print(f"Obteniendo activity files {activity_supporting_file_id}....")
    
    if activity_supporting_file_id:
      #GET ACTIVITY FILES
      activity_file_response = requests.get(f"http://localhost:8080/api/files/{activity_supporting_file_id}")

      with open(tmpdir +"/activity_files.tar.gz", 'wb') as af:
        af.write(activity_file_response.content)
    else:
      print("NO HAY ACTIVITY FILES")

    # ---------------------------------------------------------

    print(f"Submission obtenida: {solution_tar}")


    print("Actualizando submission: PROCESSING")
    response = requests.put(f"http://localhost:8080/api/submissions/{submission_id}", json={"status":"PROCESSING"})
    if response.status_code != 200:
      raise Exception(f"Error al actualizar el estado de la submission: {response.json()}")


    # ---------------------------------------------------------

    print("Ejecutando codigo en contenedor docker")
    # Lanzar ya el proceso worker para poder pasar su stdin a tarfile.open().
    # --rm --> clean up container after run
    #
    with subprocess.Popen(["docker", "run", "--rm", "--interactive", "--env", "LANG=C.UTF-8", "rpl-2.0-runner", "--lang", lang],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT) as worker:

      tar = tarfile.open(fileobj=worker.stdin, mode="w|", dereference=True)
      
      # Agrego archivos de la submission
      with tarfile.open(tmpdir + '/submission_files.tar.gz') as submission_tar:
        for member_tarinfo in submission_tar.getmembers():
          member_fileobj = submission_tar.extractfile(member_tarinfo)
          tar.addfile(tarinfo=member_tarinfo, fileobj=member_fileobj)

      # Agrego archivos de la activity
      if activity_supporting_file_id:
        with tarfile.open(tmpdir + '/activity_files.tar.gz') as activiy_files_tar:
          for member_tarinfo in activiy_files_tar.getmembers():
            member_fileobj = activiy_files_tar.extractfile(member_tarinfo)
            tar.addfile(tarinfo=member_tarinfo, fileobj=member_fileobj)

      # if activity_unit_tests:
      #   # Agrego archivo de test unitario
      #   unit_test_info = tarfile.TarInfo(name="unit_test.c")
      #   unit_test_info.size = len(activity_unit_tests)
      #   tar.addfile(tarinfo=unit_test_info, fileobj=io.BytesIO(activity_unit_tests.encode("utf-8")))

      if activity_io_tests:
        # Agrego archivo de test IO
        for i, io_test in enumerate(activity_io_tests):
          IO_test_info = tarfile.TarInfo(name=f"IO_test_{i}.txt")
          IO_test_info.size = len(io_test)
          tar.addfile(tarinfo=IO_test_info, fileobj=io.BytesIO(io_test.encode("utf-8")))

      tar.close()


      # Bloqueamos proceso hasta que el worker termine de correr la submission :)
      stdout, _ = worker.communicate()
      json_output = stdout.decode("utf-8", "replace")
      retcode = worker.wait()

      print("Resultado:\n\n")

      print(json_output)

      result = json.loads(json_output)

      # print(result)

      print("################## STDOUT ######################")
      print(result["test_run_stdout"])
      print("################## STDOUT ######################")
      print("################## STDERR ######################")
      print(result["test_run_stderr"])
      print("################## STDERR ######################")

      print(f"Código de retorno de ejecución: {retcode}")

      
      # mandar resultado (json_output/result) POST al backend
      response = requests.post(f"http://localhost:8080/api/submissions/{submission_id}/result", json=result)
      if response.status_code != 201:
        raise Exception(f"Error al postear el resultado de la submission: {response.json()}")


    # except Timeout:
      # raise Error("TIMEOUT")


if __name__ == "__main__":
  main()