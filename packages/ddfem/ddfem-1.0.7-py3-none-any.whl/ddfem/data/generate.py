# Step 1: in the doc folder run
#         make clean
#         DUNE_LOGMODULES=8 make -ij8
# Step 2: in this folder run
#         python generate.py

import os, shutil, sys
from dune.common.module import getDunePyDir
from importlib.metadata import version
femVersion = version("dune.fem")
def main():
    if len(sys.argv)>1:
        path = sys.argv[1:]
    else:
        path = ["doc"]
    docPath = os.path.join("..","..",*path)
    print(f"using modules files from {docPath}")
    if not os.path.exists(docPath):
        raise RuntimeError(f"folder {docPath} does not exist")

    dunepy = getDunePyDir()
    names = set()
    for file in os.listdir(docPath):
        filename = os.path.join(docPath,os.fsdecode(file))
        if filename.endswith(".modules"):
            with open(filename,"r") as f:
                names.update(f.readlines())

    if os.path.exists(femVersion):
        shutil.rmtree(femVersion)
    os.makedirs(femVersion)

    for name in names:
        name = name.strip()
        print(name)
        src = os.path.join(dunepy,"python","dune","generated",name+".cc")
        try:
            shutil.copy(src, femVersion)
        except FileNotFoundError:
            print(f"Error: can't copy {src}",flush=True)
            pass

if __name__ == "__main__":
    main()
