# Step 1: in the doc folder run
#         make clean
#         DUNE_LOGMODULES=8 make -ij8
# Step 2: in this folder run
#         python generate.py

import os, shutil
from dune.common.module import getDunePyDir
def main():
    dunepy = getDunePyDir()
    docPath = os.path.join("..","..","doc")
    names = set()
    for file in os.listdir(docPath):
        filename = os.path.join(docPath,os.fsdecode(file))
        if filename.endswith(".modules"):
            with open(filename,"r") as f:
                names.update(f.readlines())
    for name in names:
        name = name.strip()
        print(name)
        src = os.path.join(dunepy,"python","dune","generated",name+".cc")
        try:
            shutil.copy(src, ".")
        except FileNotFoundError:
            print(f"Error: can't copy {src}",flush=True)
            pass

if __name__ == "__main__":
    main()

