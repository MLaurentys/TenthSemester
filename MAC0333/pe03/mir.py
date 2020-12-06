import argparse
import pickle
import os
import chardet
import re

import util

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
argparser.add_argument('-A', dest='auxiliar', action='store_const',
    const=True, default=False, help='Controla o uso do indexador principal')

class MIR(util.Indexer):
    def __init__(self, parentFolder, fixedEncodeFilename, verbose):
        self.fixedEncode = {} # file -> encoding
        self.toIgnore = set() # List of files and folders
        self.index = {} # string -> list of document indexes
        self.encodeFilename = fixedEncodeFilename
        self.root = parentFolder
        self.files = []
        self.verbose = verbose
        self.wordCount = 0
        self.encodings = {} # ID -> file information

    def Build(self):
        self._ReadEncodeFile()
        self._GetFiles()
        self._CreateIndex()

    def Serialize(self):
        open(self.root + '/mir.pickle', 'w').close() # Erases old content
        with open(self.root + '/mir.pickle', 'wb') as f:
            pickle.dump(["MIR 2.0", self.files, self.index, self.encodings], f)
        print(f"The {len(self.files)} files were processed and resulted in "
            f"{self.wordCount} words, with {len(self.index.keys())} distinct "
            f"tokens. Informations saved on mir.pickle to load via pickle.")

    def _ReadEncodeFile(self):
        if self.encodeFilename == "": return
        print(f"Instruçoes ao indexador tomadas de {encodeFilename}")
        with open(encodeFilename) as f:
            lines = f.readlines()
        for line in lines:
            print(line[0:-1])
            wds = line.split()
            if line[0] != '@' or len(wds) != 2: continue
            if line[1] == 'x':
                self.toIgnore.add(os.path.abspath(self.root + wds[1]))
            elif line[1] == 'u':
                self.fixedEncode[parentFolder + wds[1]] = "utf-8"
        print()

    def _GetFiles(self):
        files = self.files
        txtReg = re.compile(".*\.txt")
        visitedDirs = set() # Set of abspaths of already listed dirs
        dirs, links = self._GetAllSubdirs(self.root, visitedDirs)
        for path in dirs: visitedDirs.add(os.path.abspath(path))
        # Traverses all links, avoiding repeated paths
        while len(links) > 0:
            link = links.pop()
            realAbsPath = os.path.abspath(os.path.realpath(link))
            if realAbsPath in visitedDirs: continue
            nd, nl = self._GetAllSubdirs(self.root, visitedDirs)
            nd.append(link)
            nvd = set()
            for path in nd:
                nvd.add(os.path.abspath(path))
            visitedDirs.update(nvd)
            links.update(nl)
        # Creates the list of documents located in the considered folders
        dirs = sorted(list(visitedDirs))
        dirs = [os.path.relpath(dir, './') + '/' for dir in dirs]
        for dir in dirs:
            for item in os.listdir(dir):
                file = dir + item
                if not (os.path.isfile(file) and txtReg.match(item)): continue
                if os.path.abspath(file) in self.toIgnore:
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
            f"{self.root}")
        [print(i, os.path.relpath(files[i], self.root)) for i in range(len(files))]
        print(f"Foram encontrados {len(files)} documentos.\n")
        for i, file in enumerate(files):
            self.encodings[i] = {"modificado": os.path.getmtime(file)}

    def _GetAllSubdirs(self, parent, visited):
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
            if absPath in self.toIgnore:
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

    def _CreateIndex(self):
        files = self.files; invertedIndex = self.index; encodings = self.encodings
        knownTokens = set() #set of words already tokenized
        if self.verbose: print("  ID  |  Encoding  | Confidence |   Size   | File")
        for i in range (len(files)):
            fileTokens = set()
            fStat, words = self._ReadFile(files[i])
            enc = fStat['encoding']; confi = fStat['confidence']
            size = fStat['tamanho']
            encodings[i]['encoding'] = enc; encodings[i]['confidence'] = confi
            encodings[i]['tamanho'] = size; encodings[i]['errors'] = fStat["errors"]
            self.wordCount += len(words)
            if self.verbose:
                print(f" {i:{4}} | {str(enc):{10}} | {confi:{10}}"\
                    f" | {size:{8}}"\
                    f" | {os.path.relpath(files[i], self.root)}")
            for wd in words:
                token = self._MakeToken(wd)
                if token == '': continue
                elif token in knownTokens:
                    if token not in fileTokens:
                        invertedIndex[token].append([i,1]) # 1 is the #occurances
                        fileTokens.add(token)
                    else:
                        invertedIndex[token][-1][1] += 1 # adds to #occurances
                else:
                    invertedIndex[token] = [[i,1]]
                    fileTokens.add(token)
                    knownTokens.add(token)
            for token in fileTokens:
                invertedIndex[token][-1][1] /= len(words) # transforms #occurances
                                                          #  in term frequence
        if args.showToken:
            for t in knownTokens: print(t)

    def _MakeToken (self, word): return word.lower()

    # Returns the encoding information and the words a file contains
    def _ReadFile (self, file):
        fStat = self._GetEncode(file)
        with open(file, encoding=fStat["encoding"], errors=fStat["errors"]) as f:
            words = f.read().split()
        generatedWords = []
        for wd in words:
            generatedWords += self._StripPunctuation(wd)
        return fStat, generatedWords

    def _GetEncode(self, filename):
        enc = self.fixedEncode
        if filename in enc.keys():
            return {'encoding':enc[filename], 'confidence':1, "errors":"strict"}
        with open(filename, 'rb') as f:
            encode = chardet.detect(f.read(MAXSIZE))
            if os.stat(filename).st_size > MAXSIZE and encode['encoding'] == 'ascii':
                encode['encoding'] = "utf-8"
                encode['confidence'] = 0.4
                er = "mixed"
            elif encode['confidence'] < 0.63: er = 'replace'
            else: er = 'strict'
            encode["errors"] = er
        encode["tamanho"] = os.path.getsize(filename)
        return encode

    def _StripPunctuation (self, wd):
        return re.sub(r'([^\w\s]|\d|_)+', ' ', wd).split()

class MIRA(MIR):
    def __init__(self, parentFolder, fixedEncodeFilename, verbose):
        super().__init__(parentFolder, fixedEncodeFilename, verbose)
        princ = util.LoadData(parentFolder, True)
        if princ is None:
            print("Indexamento principal nao encontrado. Abortando...")
            exit(1)
        self.mainFiles = princ[util.LISTFILES]
        encs = princ[util.ENCODINGS]
        self.mainFilesModified = [encs[i]['modificado']
                                       for i in range(len(self.mainFiles))]

    def Build(self):
        self._ReadEncodeFile()
        self._GetFiles()
        self._FixFiles()
        self._CreateIndex()

    def _FixFiles(self):
        mf = self.mainFiles
        f = self.files
        indexed = set(f)
        found = set(mf)
        self.newFiles = indexed - found
        self.deletedFiles = found - indexed
        self.keptFiles = indexed.intersection(found)
        modified = []
        timeIndex = {}
        timeFiles = {}
        for i in range (len(mf)):
            if mf[i] in self.keptFiles:
                timeIndex[mf[i]] = self.mainFilesModified[i]
        for i in range (len(f)):
            if f[i] in self.keptFiles:
                timeFiles[f[i]] = self.encodings[i]['modificado']
        for file in self.keptFiles:
            if timeIndex[file] != timeFiles[file]:
                modified.append(file)
        self.modified = set(modified)
        print(f"De {len(mf)} para {len(f)}, foram acrescentados {len(self.newFiles)}"\
              f" arquivos novos e {len(self.deletedFiles)} removidos.")
        print(f"Permaneceram {len(self.keptFiles)}, dos quais {len(self.modified)}"\
              f" foram modificados.")
        self.files = sorted(list(self.modified.union(self.newFiles)))

    def Serialize(self):
        open(self.root + '/mira.pickle', 'w').close() # Erases old content
        open(self.root + '/mira.rem', 'w').close() # Erases old content
        with open(self.root + '/mira.rem', 'wb') as f:
            pickle.dump(list(self.deletedFiles), f)
        with open(self.root + '/mira.pickle', 'wb') as f:
            pickle.dump(["MIR 2.0", self.files, self.index, self.encodings], f)
        print(f"The {len(self.files)} files were processed and resulted in "
            f"{self.wordCount} words, with {len(self.index.keys())} distinct "
            f"tokens. Informations saved on mira.pickle and mira.rem to load "
            f"via pickle.")


def mir (args):
    parentFolder = args.dir if args.dir[-1] == '/' else args.dir + '/'
    if args.auxiliar:
        indexer = MIRA(parentFolder, args.encodeFile, args.verbose)
    else:
        indexer = MIR(parentFolder, args.encodeFile, args.verbose)
    indexer.Build()
    indexer.Serialize()


if __name__ == "__main__":
    args = argparser.parse_args()
    mir(args)
