import argparse
import pickle
import os
import chardet
import re

import util
import indexer
import auxiliar_indexer

# Lists relevant or required command-line options
argparser = argparse.ArgumentParser()
argparser.add_argument(
    "dir",
    type=str,
    help=("Caminho de diretorio com arquivos a serem tokenizados"),
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
    "--token",
    dest="showToken",
    action="store_const",
    const=True,
    default=False,
    help="Controla impressao dos tokens gerados",
)
argparser.add_argument(
    "-@",
    nargs="?",
    dest="encodeFile",
    default="",
    help="Informa arquivo lista de encodings fixos",
)
argparser.add_argument(
    "-A",
    dest="auxiliar",
    action="store_const",
    const=True,
    default=False,
    help="Controla o uso do indexador principal",
)


def mir(args):
    parentFolder = args.dir if args.dir[-1] == "/" else args.dir + "/"
    if args.auxiliar:
        indexer = auxiliarIndexer.MIRA(
            parentFolder, args.encodeFile, args.verbose, args.showToken
        )
    else:
        indexer = indexer.MIR(
            parentFolder, args.encodeFile, args.verbose, args.showToken
        )
    indexer.Build()
    indexer.Serialize()


if __name__ == "__main__":
    args = argparser.parse_args()
    mir(args)
