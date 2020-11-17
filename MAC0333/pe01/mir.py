import argparse
import pickle
import os
import chardet
import re

MAXSIZE=100000

# Lists relevant or required command-line options
argparser = argparse.ArgumentParser()
argparser.add_argument("dir", type=str, help=(
    "Caminho de diretorio com arquivos a serem tokenizados"))
argparser.add_argument('-v', '--verbose', dest='verbose', action='store_const',
    const=True, default=False, help='Controla impressao de informacoes para debug')
argparser.add_argument('-t', '--token', dest='showToken', action='store_const',
    const=True, default=False, help='Controla impressao dos tokens gerados')
argparser.add_argument('-@', nargs='?', dest='encodeFile', default="",
    help='Informa arquivo lista de encodings fixos')

# Returns a list of dirs and a list of links to directories
def GetAllSubdirs (parent, toIgnore, visited):
    # Initializes useful variables
    links = set()
    dirs = [parent]; hsDirs = set(os.path.abspath(parent))
    i = 0
    # Creates list with directories accessible from the parent folder
    while (i < len(dirs)):
        newDirs = []
        #print("LDIR: " + dirs[i])
        absPath = os.path.abspath(dirs[i])
        #relpath = os.path.relpath(dirs[i], parent)
        if absPath in visited:
            dirs.pop(i)
            continue
        if absPath in toIgnore:
            print(f"Diretório {absPath} excluı́do da indexaçao")
            dirs.pop(i)
            i += 1
            continue
        for arq in os.listdir(dirs[i]):
            item = dirs[i] + arq
            if os.path.isdir(item):
                if os.path.islink(item):
                    links.add(os.path.abspath(item))
                else:
                    newDirs.append(item + '/')
                    hsDirs.add(os.path.abspath(item))
        dirs += newDirs; i += 1
    return dirs, links

# Given a folder, returns all files accessible from that folder
def GetFiles(parentFolder, toIgnore):
    txtReg = re.compile(".*\.txt")
    visitedDirs = set() # Set of abspaths of already listed dirs
    dirs, links = GetAllSubdirs(parentFolder, toIgnore, visitedDirs)
    for path in dirs: visitedDirs.add(os.path.abspath(path))
    # Traverses all links, avoiding repeated paths
    while len(links) > 0:
        link = links.pop()
        realAbsPath = os.path.abspath(os.path.realpath(link))
        if realAbsPath in visitedDirs: continue
        nd, nl = GetAllSubdirs(parentFolder, toIgnore, visitedDirs)
        nd.append(link)
        nvd = set()
        for path in nd:
            nvd.add(os.path.abspath(path))
        visitedDirs.update(nvd)
        links.update(nl)
    # Creates the list of documents located in the considered folders
    files = []
    dirs = sorted(list(visitedDirs))
    dirs = [os.path.relpath(dir, './') + '/' for dir in dirs]
    for dir in dirs:
        for item in os.listdir(dir):
            file = dir + item
            if not (os.path.isfile(file) and txtReg.match(item)): continue
            if os.path.abspath(file) in toIgnore:
                print(f"Arquivo {item} excluı́do da indexaçao")
            else:
                files.append(file)
    files = sorted(files)
    # Removes links to files that are already considered
    for i in range (len(files)):
        if os.path.islink(files[i]):
            if os.readlink(files[i])[0:2] != "..":
                files.pop(i)
    # Prints requested output
    print(f"Lista de arquivos .txt encontrados na sub-árvore do diretório: "\
          f"{parentFolder}")
    [print(i, os.path.relpath(files[i], parentFolder)) for i in range(len(files))]
    print(f"Foram encontrados {len(files)} documentos.\n")
    return files

def MakeToken (word): return word.lower()

def GetEncode(filename, fixed):
    if filename in fixed.keys():
        return {'encoding':fixed[filename], 'confidence':1, "errors":"strict"}
    with open(filename, 'rb') as f:
        encode = chardet.detect(f.read(MAXSIZE))
        if os.stat(filename).st_size > MAXSIZE and encode['encoding'] == 'ascii':
            encode['encoding'] = "utf-8"
            encode['confidence'] = 0.4
            er = "mixed"
        elif encode['confidence'] < 0.63: er = 'replace'
        else: er = 'strict'
        encode["errors"] = er
    return encode

def StripPunctuation (wd): return re.sub(r'([^\w\s]|\d|_)+', ' ', wd).split()

# Returns the encoding information and the words a file contains
def ReadFile (file, verbose, fixed):
    fStat = GetEncode(file, fixed)
    with open(file, encoding=fStat["encoding"], errors=fStat["errors"]) as f:
        words = f.read().split()
    generatedWords = []
    for wd in words:
        generatedWords += StripPunctuation(wd)
    return fStat['encoding'], float(fStat['confidence'])*100, generatedWords

# Serializes requested information via pickle
def Serialize (parentFolder, docs, invertedIndex, encodings, wdC):
    open(parentFolder + '/mir.pickle', 'w').close() # Erases old content
    with open(parentFolder + '/mir.pickle', 'wb') as f:
        pickle.dump(["MIR 1.0", docs, invertedIndex, encodings], f)
    print(f"The {len(docs)} files were processed and resulted in "
          f"{wdC} words, with {len(invertedIndex.keys())} distinct "
          f"tokens. Informations saved on mir.pickle to load via pickle.")

# Creates inverted index and serializes the requested information
def CreateIndex (documents, parentFolder, verbose, fixed):
    wordCount = 0
    knownTokens = set() #set of words already tokenized
    invertedIndex = {} # string -> list of document indexes
    encodings = {} # ID -> enconding utilizado
    if verbose: print("  ID  |  Encoding  | Confidence |   Size   | File")
    for i in range (len(documents)):
        fileTokens = set()
        encodings[i], confidence, words = ReadFile(documents[i], verbose, fixed)
        wordCount += len(words)
        if verbose:
            print(f" {i:{4}} | {str(encodings[i]):{10}} | {confidence:{10}} |"\
                  f" {os.stat(documents[i]).st_size:{8}} |"\
                  f" {os.path.relpath(documents[i], parentFolder)}")
        for wd in words:
            token = MakeToken(wd)
            if token == '': continue
            elif token in knownTokens:
                if token not in fileTokens:
                    invertedIndex[token].append(i)
                    fileTokens.add(token)
            else:
                invertedIndex[token] = [i]
                fileTokens.add(token)
                knownTokens.add(token)
    if args.showToken:
        for t in knownTokens: print(t)
    Serialize(parentFolder, documents, invertedIndex, encodings, wordCount)
    return invertedIndex

# Reads decode rule file
def InterpretEncodeFile (encodeFile, parentFolder):
    if encodeFile == "": return [],{}
    toIgnore = set() # List of files and folders
    fixedEnc = {} # file -> encoding
    print(f"Instruçoes ao indexador tomadas de {encodeFile}")
    with open(encodeFile) as f:
        lines = f.readlines()
    for line in lines:
        print(line[0:-1])
        wds = line.split()
        if line[0] != '@' or len(wds) != 2: continue
        if line[1] == 'x':
            toIgnore.add(os.path.abspath(parentFolder + wds[1]))
        elif line[1] == 'u':
            fixedEnc[parentFolder + wds[1]] = "utf-8"
    print()
    return sorted(toIgnore), fixedEnc

def mir (args):
    parentFolder = args.dir[-1] if args.dir[-1] == '/' else args.dir + '/'
    excluded, fixed = InterpretEncodeFile(args.encodeFile, parentFolder)
    files = GetFiles(parentFolder, excluded)
    index = CreateIndex(files, parentFolder, args.verbose, fixed)

if __name__ == "__main__":
    args = argparser.parse_args()
    mir(args)
