import argparse
import glob
import pickle
import os
import chardet
import re

# Lists relevant or required command-line options
argparser = argparse.ArgumentParser()
argparser.add_argument("dir", type=str, help=(
    "Path to parent directory that keep the files"))
argparser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
    const=True, default=False, help='Makes the program print debug information')
argparser.add_argument('-t', '--token', dest='showToken', action='store_const',
    const=True, default=False, help='Makes the program output generated tokens')

def GetFiles(parentFolder):
    dirs = [parentFolder]; hsDirs = set(os.path.abspath(parentFolder))
    i = 0
    while (i < len(dirs)):
        newDirs = []
        for arq in os.listdir(dirs[i]):
            item = dirs[i] + '/' + arq
            if os.path.isdir(item):
                if os.path.islink(item):
                    rPath = os.path.realpath(os.path.join(dirs[i], os.readlink(item)))
                    if not rPath in hsDirs:
                        newDirs.append(item)
                        hsDirs.add(rPath)
                else:
                    newDirs.append(item)
                    hsDirs.add(os.path.abspath(item))
        dirs += newDirs; i += 1
    txtReg = re.compile(".*\.txt")
    files = sorted([dir + '/' + item for dir in dirs for item in os.listdir(dir)
                if os.path.isfile(dir + '/' + item) and txtReg.match(item)])
    for i in range (len(files)):
        if os.path.islink(files[i]):
            files[i] = parentFolder + "/" + os.readlink(files[i])
    print(f"Lista de arquivos .txt encontrados na sub-árvore do diretório: "\
          f"{parentFolder}")
    [print(i, files[i]) for i in range(len(files))]
    print(f"Foram encontrados {len(files)} arquivos.\n")
    return files

def MakeToken (word):
    token = word.lower()
    return token

def ReadFile (file, verbose):
    def GetEncode(filename):
        with open(filename, 'rb') as f:
            return chardet.detect(f.read())
    fStat = GetEncode(file)
    encode = fStat['encoding']
    confidence = float(fStat['confidence'])*100
    errorHandling = "strict" if confidence >= 63.0 else "replace"
    with open(file, encoding=encode, errors=errorHandling) as f:
        words = f.read().split()
    generatedWords = []
    for wd in words:
        generatedWords += StripPunctuation(wd)
    return encode, confidence, generatedWords

def StripPunctuation (word):
    return re.sub(r'([^\w\s]|\d|_)+', ' ', word).split()

def CreateIndex (documents, parentFolder, verbose):
    if verbose: print("Creating Index:")
    wordCount = 0; badDecCount = 0
    knownTokens = set() #set of words already tokenized
    invertedIndex = {} # string -> list of document indexes
    encodings = {} # ID -> enconding utilizado
    for i in range (len(documents)):
        fileTokens = set()
        encodings[i], confidence, words = ReadFile(documents[i], verbose)
        if confidence < 63: badDecCount += 1
        wordCount += len(words)
        if verbose:
            print(f"File: {os.path.relpath(documents[i],parentFolder)}"\
                  f":\nID: {i}\nSize: {os.stat(documents[i]).st_size}\n"\
                  f"Encoding: {encodings[i]}\nConfidence: {confidence}\n")
        for wd in words:
            token = MakeToken(wd)
            if token == '': continue
            if token in knownTokens:
                if token not in fileTokens:
                    invertedIndex[token].append(i)
                    fileTokens.add(token)
            else:
                invertedIndex[token] = [i]
                fileTokens.add(token)
                knownTokens.add(token)
    if args.showToken:
        for t in knownTokens: print(t)
    open(parentFolder + '/mir.pickle', 'w').close() # Erases old content
    with open(parentFolder + '/mir.pickle', 'wb') as f:
        pickle.dump([documents, invertedIndex, encodings], f)
        print(f"The {len(documents)} files were processed and resulted in "
              f"{wordCount} words, with {len(invertedIndex.keys())} "
              f"distinc tokens. Informations saved on mir.pickle to load via "
              f"pickle")
    print(f"{badDecCount} files with low decoding confidence")
    return invertedIndex


def mir (args):
    parentFolder = args.dir
    files = GetFiles(parentFolder)
    index = CreateIndex(files, parentFolder, args.verbose)

if __name__ == "__main__":
    args = argparser.parse_args()
    mir(args)
