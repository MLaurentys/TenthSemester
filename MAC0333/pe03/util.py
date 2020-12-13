import pickle
import os
from sys import maxsize
import re

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


def GetShortestIntervalIntersectingTwoLists(l1, l2):
    minDist = maxsize
    minInterval = [0, maxsize]
    i = 0
    j = 0
    while i < len(l1) and j < len(l2):
        dis = abs(l2[j] - l1[i])
        if dis < minDist:
            minDist = dis
            minInterval = [min(l2[j], l1[i]), max(l2[j], l1[i])]
        if dis == 1:
            break
        if l1[i] < l2[j]:
            i += 1
        else:
            j += 1
    return minInterval


def GetSmallestInterval(lists):
    minDist = maxsize
    minInterval = [0, maxsize]
    for i in range(len(lists)):
        for j in range(i + 1, len(lists)):
            inter = GetShortestIntervalIntersectingTwoLists(lists[i], lists[j])
            if len(inter) < minDist:
                minInterval = inter
                minDist = len(inter)
    return minInterval


def StripPunctuation(word):
    return re.sub(r"([^\w\s]|\d|_)+", " ", word).split()


# Reads serialized file
def LoadData(parentFolder, onlyPrim):
    pfile = parentFolder + "mir.pickle"
    afile = parentFolder + "mira.pickle"
    rmfile = parentFolder + "mira.rem"
    if not os.path.exists(pfile):
        print("No principal index found... Skipping")
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