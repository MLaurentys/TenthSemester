import argparse
import pickle
import os
import re

CHARSET = 0
LISTFILES = CHARSET + 1
INDEX = CHARSET + 2
ENCODINGS = CHARSET + 3


# Lists relevant or required command-line options
argparser = argparse.ArgumentParser()
argparser.add_argument("dir", type=str, help=(
    "Caminho de diretorio com dados serializados"))
argparser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
    const=True, default=False, help='Controla impressao de informacoes para debug')
argparser.add_argument('-t', '--topo', dest='topo', type=int,
    help='Imprime os \'TOPO\' tokens mais frequentes')
argparser.add_argument('-r', '--regex', dest='regex',
    help='Imprime apenas TOKENS que sigam o padrao')
argparser.add_argument('-R', '--regexneg', dest='regexneg',
    help='Imprime apenas TOKENS que NAO sigam o padrao')
argparser.add_argument('queryTokens', nargs='*', default=[],
    help='Lista de termos da consulta conjuntiva' )

# Reads serialized file
def loadData (parentFolder):
    pkFile = parentFolder + '/mir.pickle'
    f =  open(pkFile, 'rb')
    w = pickle.load(f)
    f.close()
    print(f"{w[CHARSET]} de {pkFile}\nPickle Information:"\
          f"\n{len(w[LISTFILES])} documents\n{len(w[INDEX])} tokens\n")
    return w

# Handles -t option
def PrintTopo(index, num, match=None, negMatch=None):
    def compareValue (item): return len(index[item])
    def compareValue2 (item): return str(item)
    keys = index.keys()
    keys = sorted(sorted(keys, key=compareValue2, reverse=True), key=compareValue)
    if match is not None:
        regex = re.compile(match)
        keys = [k for k in keys if regex.match(k)]
    if negMatch is not None:
        regex = re.compile(negMatch)
        keys = [k for k in keys if not regex.match(k)]
    print(f"{len(keys)} tokens matched regex restrictions")
    print(" DF |    Token    | Lista de incidencia")
    for i in range (len(keys)-1, len(keys)-num-1, -1):
        print(f" {len(index[keys[i]]):{2}} | {keys[i]:{11}} | {index[keys[i]]}")
    print()

# Handles SELECT query
def PrintSelect(tokens, index, files):
    print("Conjugaçao das listas de termos")
    sets = []
    print(" DF |    Token    | Lista de incidencia")
    for token in tokens:
        if token not in index.keys():
            print(f" -- | {token:{11}} | -----")
            sets.append(set())
        else:
            print(f" {len(index[token]):{2}} | {token:{11}} | {index[token]}")
            sets.append(set([ind for ind in index[token]]))
    res = sets[0]
    for st in sets:
        res = res.intersection(st)
    print(f"Existem {len(res)} documentos com os {len(tokens)} termos:")
    for doc in res: print(f"{doc}: {files[doc]}")


def mirs (args):
    parentFolder = args.dir[-1] if args.dir[-1] == '/' else args.dir + '/'
    filesInfo = loadData(parentFolder)
    if args.topo is not None:
        PrintTopo(filesInfo[INDEX], args.topo, args.regex, args.regexneg)
    if args.queryTokens != []:
        PrintSelect(args.queryTokens, filesInfo[INDEX], filesInfo[LISTFILES])

if __name__ == "__main__":
    args = argparser.parse_args()
    mirs(args)
