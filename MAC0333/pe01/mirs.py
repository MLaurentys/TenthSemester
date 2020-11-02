import argparse
import pickle
import os
import re

CHARSET = -1
LISTFILES = CHARSET + 1
INDEX = CHARSET + 2
ENCODINGS = CHARSET + 3


# Enforces required command-line options
argparser = argparse.ArgumentParser()

argparser.add_argument("dir", type=str, help=(
    "Path to parent directory that keep the pickle file"))
argparser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
    const=True, default=False, help='Makes the program print debug information')
argparser.add_argument('-t', '--topo', dest='topo', type=int,
    help='Output most frequent \'TOPO\' tokens')
argparser.add_argument('-r', '--regex', dest='regex',
    help='Only print TOKEN results matching pattern')
argparser.add_argument('-R', '--regexneg', dest='regexneg',
    help='Only print TOKEN results NOT matching pattern')
argparser.add_argument('-l','--list', nargs='*', dest="queryTokens",
    help='List of tokens to query')

def loadData (parentFolder):
    f =  open(parentFolder + '/mir.pickle', 'rb')
    w = pickle.load(f)
    f.close()
    print(f"Pickle Information:\n{len(w[LISTFILES])} documents\n"
          f"{len(w[INDEX])} tokens\n")
    return w

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
    print(" DF |  Token  | List")
    for i in range (len(keys)-1, len(keys)-num-1, -1):
        print(f" {len(index[keys[i]])} | {keys[i]} {index[keys[i]]}\n")

def PrintSelect(tokens, index, files):
    sets = [set([ind for ind in index[token]]) for token in tokens]
    res = sets[0]
    for st in sets:
        res = res.intersection(st)
    print(f"Existem {len(res)} documentos com os {len(tokens)} termos:")
    [print(f"{doc}: {files[doc]}") for doc in res]


def mirs ():
    args = argparser.parse_args()
    parentFolder = args.dir
    filesInfo = loadData(parentFolder)
    if args.topo is not None:
        PrintTopo(filesInfo[INDEX], args.topo, args.regex, args.regexneg)
    if args.queryTokens is not None:
        PrintSelect(args.queryTokens, filesInfo[INDEX], filesInfo[LISTFILES])

if __name__ == "__main__":
    mirs()