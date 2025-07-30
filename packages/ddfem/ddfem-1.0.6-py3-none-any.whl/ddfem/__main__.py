import sys, os
try:
    import dune
except ImportError:
    dune = None
import ddfem

def main():
    if dune:
        from dune.fem.utility import FemThreadPoolExecutor
        from dune.generator import builder
        builder.initialize()

        dataPath = os.path.join(ddfem.__path__[0],"data")
        with FemThreadPoolExecutor(max_workers=8) as executor:
            for file in os.listdir(dataPath):
                filename = os.path.join(dataPath,os.fsdecode(file))
                if filename.endswith(".cc"):
                    with open(filename,"r") as f:
                        executor.submit( builder.load, file.replace(".cc",""), f.read(), None )

if __name__ == "__main__":
    main()

