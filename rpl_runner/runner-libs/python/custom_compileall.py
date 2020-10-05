import compileall
import sys

sys.stdout = sys.stderr
compileall.compile_dir(".", force=True, quiet=1)  # Only print errors, all to stderr
sys.stdout = sys.__stdout__

import os
import shutil

DIR = os.getcwd()

# Remove all python files
for file in os.listdir(DIR):
    if file.endswith(".py"):
        os.remove(os.path.join(DIR, file))

pycache_dir = os.path.join(DIR, "__pycache__")

# rename pyc files extracting the cpython part
# move files from __pycache__ to current dir
for filename in os.listdir(pycache_dir):
    if filename.endswith(".pyc"):
        to_remove = filename.split(".")[-2]
        new_name = filename.replace("." + to_remove, "")
        os.rename(
            os.path.join(pycache_dir, filename), os.path.join(pycache_dir, new_name)
        )
        shutil.move(os.path.join(pycache_dir, new_name), DIR)

# delete old pycache files
for folder in os.listdir(DIR):
    if folder.startswith("__pycache__"):
        os.rmdir(os.path.join(DIR, folder))
