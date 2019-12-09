import tempfile
import subprocess
import tarfile
import time
import json

def main():
	ejecutar(10)


def ejecutar(submission_id):
  """Función principal del script.
  """
  with tempfile.TemporaryDirectory(prefix="corrector.") as tmpdir:
    
  	solution_tar = "tar_assignment_solved_c.tar.gz"  # Obtener a partir del id del mensaje
  	#Cuando salgo de aca se deberia eliminar todo lo relacionado con esta entrega ya que vive en este directorio temporal

  	print(f"Obteniendo submission {submission_id}....")
  	time.sleep(1) #ahre
  	print(f"Submission obtenida: {solution_tar}")

  	print("Ejecutando codigo en contenedor docker")
  	# Lanzar ya el proceso worker para poder pasar su stdin a tarfile.open().
  	# --rm --> clean up container after run
  	# 
  	with subprocess.Popen(["docker", "run", "--rm", "--interactive", "--env", "LANG=C.UTF-8", "rpl-2.0-runner", "--lang", "c"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT) as worker:


  		tar = tarfile.open(fileobj=worker.stdin, mode="w|", dereference=True)
  		tar.add("input.txt")
  		tar.add("output.txt")
  		tar.add("test_file.c")

  		tar.close()


  		stdout, _ = worker.communicate()
  		output = stdout.decode("utf-8", "replace")
  		retcode = worker.wait()

  		print("Resultado:\n\n")

  		result = json.loads(output)

  		print(result)
  		print(result["stdout"])
  		print(result["stderr"])

  		print(f"Código de retorno de ejecución: {retcode}")

  		# mandar resultado (output) al backend


    # except Timeout:
      # raise Error("TIMEOUT")


if __name__ == "__main__":
	main()