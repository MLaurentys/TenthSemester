import argparse
import os

import util
import retriever

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
    default=0,
    dest="sortAlg",
    help="Selects sorting algorithm [0-5] used to define most common tokens",
)
argparser.add_argument(
    "-a",
    type=int,
    default=-1,
    dest="amountToShow",
    help="How many tokens fitting query are shown",
)
argparser.add_argument(
    "queryTokens",
    nargs="*",
    default=[],
    help="Lista de termos da consulta conjuntiva",
)


def mirs(args):
    parentFolder = args.dir if args.dir[-1] == "/" else args.dir + "/"
    primInfo, aInfo, rmInfo = util.LoadData(parentFolder, False)
    myRetriever = retriever.Retriever(
        primInfo, args.sortAlg, args.amountToShow, args.verbose, aInfo, rmInfo
    )
    if args.topo is not None:
        myRetriever.PrintTopo(args.topo, args.regex, args.regexneg)
    if args.queryTokens != []:
        myRetriever.HandleSelect(args.queryTokens)


if __name__ == "__main__":
    args = argparser.parse_args()
    mirs(args)
