import argparse
import os
import re

import util

# Lists relevant or required command-line options
argparser = argparse.ArgumentParser()
argparser.add_argument(
    "dir", type=str, help=("Caminho de diretorio com dados serializados")
)
argparser.add_argument(
    "-v",
    "--verbose",
    dest="verbose",
    action="store_const",
    const=True,
    default=False,
    help="Controla impressao de informacoes para debug",
)
argparser.add_argument(
    "-t",
    "--topo",
    dest="topo",
    type=int,
    help="Imprime os 'TOPO' tokens mais frequentes",
)
argparser.add_argument(
    "-r",
    "--regex",
    dest="regex",
    help="Imprime apenas TOKENS que sigam o padrao",
)
argparser.add_argument(
    "-R",
    "--regexneg",
    dest="regexneg",
    help="Imprime apenas TOKENS que NAO sigam o padrao",
)
argparser.add_argument(
    "-o",
    type=int,
    dest="regexAlg",
    help="Selects sorting algorithm [0-5] used to define most common tokens",
)
argparser.add_argument(
    "queryTokens",
    nargs="*",
    default=[],
    help="Lista de termos da consulta conjuntiva",
)

# Handles -t option
def PrintTopo(index, aInd, indMap, aOff, num, match=None, negMatch=None):
    def compareValue(item):
        df = 0  # document frequence
        if item in aKeys:
            df = len(aInd[item])
        if item in pKeys:
            for doc in index[item]:
                if indMap[doc[0]] != -1:
                    df += 1
        return df

    def compareValue2(item):
        return str(item)  # len + alphabetical

    def getIncidence(i):
        incidence = [
            indMap[ind[0]] for ind in index[keys[i]] if indMap[ind[0]] != -1
        ]
        incidence += [(ind[0] + aOff) for ind in aInd[keys[i]]]
        return incidence

    aKeys = set(aInd.keys())
    pKeys = set(index.keys())
    keys = list(pKeys.union(aKeys))
    keys = sorted(
        sorted(keys, key=compareValue2, reverse=True), key=compareValue
    )
    if match is not None:
        regex = re.compile(match)
        keys = [k for k in keys if regex.match(k)]
    if negMatch is not None:
        regex = re.compile(negMatch)
        keys = [k for k in keys if not regex.match(k)]
    print(f"{len(keys)} tokens matched regex restrictions")
    print(" DF |    Token    | Lista de incidencia")
    for i in range(len(keys) - 1, max(0,len(keys) - num - 1), -1):
        print(
            f" {len(index[keys[i]]):{2}} | {keys[i]:{11}} | {getIncidence(i)}"
        )
    print()


# Handles SELECT query
def PrintSelect(tokens, pIndex, pFiles, aIndex, aFiles, indMap, aOffset):
    sets = []
    aKeys = set(aIndex.keys())
    pKeys = set(pIndex.keys())
    keys = pKeys.union(aKeys)
    print("Conjugaçao das listas de termos")
    print("  DF  |    Token    | Lista de incidencia")
    for token in tokens:
        if token not in keys:
            print(f" ---- | {token:{11}} | -----")
            sets.append(set())
        else:
            pInc = []
            aInc = []
            if token in pKeys:
                pInc = [
                    indMap[ind[0]]
                    for ind in pIndex[token]
                    if indMap[ind[0]] != -1
                ]
            if token in aKeys:
                aInc = [ind[0] + aOffset for ind in aIndex[token]]
            print(f" {len(pIndex[token]):{4}} | {token:{11}} | {pInc + aInc}")
            sets.append(set([ind for ind in pInc + aInc]))
    print(sets)
    res = sets[0]
    for st in sets:
        res = res.intersection(st)
    print(f"Existem {len(res)} documentos com os {len(tokens)} termos:")
    for doc in res:
        if doc >= aOffset:
            print(f"{doc}: {aFiles[doc - aOffset]}")
        else:
            print(f"{doc}: {pFiles[doc]}")


# Linear time on the NUMBER OF FILES in prim+aux+rem
# Fixed prim (considered in/out) and builds indMap
def BuildInfo(prim, aux, rem):
    files = prim[util.LISTFILES]
    index = prim[util.INDEX]
    enc = prim[util.ENCODINGS]
    keys = index.keys()
    # Removes 'rem' from prim -> indexMap to be used in queries
    removed = set(rem)
    toRem = []
    indMap = {
        i: i for i in range(len(files))
    }  # Maps initial file ID to final ID
    offset = 0
    # Treats modified entries as removed files
    fs = set(aux[util.LISTFILES])
    modified = fs.intersection(set(files))
    for i in range(len(files)):
        if files[i] in removed or files[i] in modified:
            toRem.append(i)
            indMap[i] = -1  # Marked because file was removed
            offset -= 1
        else:
            indMap[i] += offset
    for i in range(len(toRem) - 1, -1, -1):
        files.pop(toRem[i])
    print(f"Final list of files: ")
    for f in files + aux[util.LISTFILES]:
        print(f)
    print()
    return indMap, len(files)


def mirs(args):
    parentFolder = args.dir if args.dir[-1] == "/" else args.dir + "/"
    primInfo, aInfo, rmInfo = util.LoadData(parentFolder, False)
    indMap, aOffset = BuildInfo(primInfo, aInfo, rmInfo)
    if args.topo is not None:
        PrintTopo(
            primInfo[util.INDEX],
            aInfo[util.INDEX],
            indMap,
            aOffset,
            args.topo,
            args.regex,
            args.regexneg,
        )
    if args.queryTokens != []:
        PrintSelect(
            args.queryTokens,
            primInfo[util.INDEX],
            primInfo[util.LISTFILES],
            aInfo[util.INDEX],
            aInfo[util.LISTFILES],
            indMap,
            aOffset,
        )


if __name__ == "__main__":
    args = argparser.parse_args()
    mirs(args)
