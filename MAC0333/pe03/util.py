import pickle
import os

CHARSET = 0
LISTFILES = CHARSET + 1
INDEX = CHARSET + 2
ENCODINGS = CHARSET + 3
POSITIONAL = CHARSET + 4

# Abstract class for indexer
class Indexer:
    def __init__(self, parentFolder, fixedEncodeFile):
        raise NotImplementedError("Override me!")

    def Build(self):
        raise NotImplementedError("Override me!")

    def Serialize(self, destFile):
        raise NotImplementedError("Override me!")


# Reads serialized file
def LoadData(parentFolder, onlyPrim):
    pfile = parentFolder + "mir.pickle"
    afile = parentFolder + "mira.pickle"
    rmfile = parentFolder + "mira.rem"
    if not os.path.exists(pfile):
        return
    with open(pfile, "rb") as f:
        princ = pickle.load(f)
    print(
        f"{princ[CHARSET]} de {pfile}\nPickle Information:"
        f"\n{len(princ[LISTFILES])} documents\n{len(princ[INDEX])} tokens\n"
    )
    if onlyPrim:
        return princ
    if os.path.exists(afile):
        with open(afile, "rb") as f:
            aux = pickle.load(f)
        print(
            f"{aux[CHARSET]} de {afile}\nPickle Information:"
            f"\n{len(aux[LISTFILES])} documents\n{len(aux[INDEX])} tokens"
        )
    else:
        aux = None
    if os.path.exists(rmfile):
        with open(rmfile, "rb") as f:
            rem = pickle.load(f)
        print(
            f"\nPickle Information of {rmfile}:"
            f"\n{len(rem)} documents removed\n"
        )
    else:
        rem = None
    return princ, aux, rem