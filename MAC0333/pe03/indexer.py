import os
import pickle
import re
import chardet
import time
import numpy as np

import util

MAXSIZE = 100000


class MIR(util.Indexer):
    def __init__(self, parentFolder, fixedEncodeFilename, verbose, showToken):
        self.fixedEncode = {}  # file -> encoding
        self.toIgnore = set()  # List of files and folders
        self.index = {}  # string -> list of document indexes
        self.positionalIndex = np.array([], dtype=int)
        self.showToken = showToken
        self.encodeFilename = fixedEncodeFilename
        self.root = parentFolder
        self.files = []
        self.verbose = verbose
        self.wordCount = 0
        self.encodings = {}  # ID -> file information

    def Build(self):
        self._ReadEncodeFile()
        self._GetFiles()
        self._CreateIndex()
        self._BuildPositionalIndex()

    def Serialize(self):
        open(self.root + "/mir.pickle", "w").close()  # Erases old content
        with open(self.root + "/mir.pickle", "wb") as f:
            pickle.dump(
                [
                    "MIR 3.0",
                    self.files,
                    self.index,
                    self.encodings,
                    self.positionalIndex,
                    time.time(),
                ],
                f,
            )
        print(
            f"The {len(self.files)} files were processed and resulted in "
            f"{self.wordCount} words, with {len(self.index.keys())} distinct "
            f"tokens. Informations saved on mir.pickle to load via pickle."
        )

    def _ReadEncodeFile(self):
        if self.encodeFilename == "":
            return
        print(f"Instruçoes ao indexador tomadas de {encodeFilename}")
        with open(encodeFilename) as f:
            lines = f.readlines()
        for line in lines:
            print(line[0:-1])
            wds = line.split()
            if line[0] != "@" or len(wds) != 2:
                continue
            if line[1] == "x":
                self.toIgnore.add(os.path.abspath(self.root + wds[1]))
            elif line[1] == "u":
                self.fixedEncode[parentFolder + wds[1]] = "utf-8"
        print()

    def _GetFiles(self):
        files = self.files
        txtReg = re.compile(".*\.txt")
        visitedDirs = set()  # Set of abspaths of already listed dirs
        dirs, links = self._GetAllSubdirs(self.root, visitedDirs)
        for path in dirs:
            visitedDirs.add(os.path.abspath(path))
        # Traverses all links, avoiding repeated paths
        while len(links) > 0:
            link = links.pop()
            realAbsPath = os.path.abspath(os.path.realpath(link))
            if realAbsPath in visitedDirs:
                continue
            nd, nl = self._GetAllSubdirs(self.root, visitedDirs)
            nd.append(link)
            nvd = set()
            for path in nd:
                nvd.add(os.path.abspath(path))
            visitedDirs.update(nvd)
            links.update(nl)
        # Creates the list of documents located in the considered folders
        dirs = sorted(list(visitedDirs))
        dirs = [os.path.relpath(dir, "./") + "/" for dir in dirs]
        for dir in dirs:
            for item in os.listdir(dir):
                file = dir + item
                if not (os.path.isfile(file) and txtReg.match(item)):
                    continue
                if os.path.abspath(file) in self.toIgnore:
                    print(f"Arquivo {item} excluı́do da indexaçao")
                else:
                    files.append(file)
        files = sorted(files)
        # Removes links to files that are already considered
        for i in range(len(files)):
            if os.path.islink(files[i]):
                if os.readlink(files[i])[0:2] != "..":
                    files.pop(i)
        # Prints requested output
        print(
            f"Lista de arquivos .txt encontrados na sub-árvore do diretório: "
            f"{self.root}"
        )
        [
            print(i, os.path.relpath(files[i], self.root))
            for i in range(len(files))
        ]
        print(f"Foram encontrados {len(files)} documentos.\n")
        for i, file in enumerate(files):
            self.encodings[i] = {"modificado": os.path.getmtime(file)}

    def _GetAllSubdirs(self, parent, visited):
        # Initializes useful variables
        links = set()
        dirs = [parent]
        hsDirs = set(os.path.abspath(parent))
        i = 0
        # Creates list with directories accessible from the parent folder
        while i < len(dirs):
            newDirs = []
            # print("LDIR: " + dirs[i])
            absPath = os.path.abspath(dirs[i])
            # relpath = os.path.relpath(dirs[i], parent)
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
                        newDirs.append(item + "/")
                        hsDirs.add(os.path.abspath(item))
            dirs += newDirs
            i += 1
        return dirs, links

    def _CreateIndex(self):
        files = self.files
        invertedIndex = self.index
        encodings = self.encodings
        knownTokens = set()  # set of words already tokenized
        if self.verbose:
            print("  ID  |  Encoding  | Confidence |   Size   | File")
        for i in range(len(files)):
            fileTokens = set()
            fStat, words = self._ReadFile(files[i])
            enc = fStat["encoding"]
            confi = fStat["confidence"]
            size = fStat["tamanho"]
            encodings[i]["encoding"] = enc
            encodings[i]["confidence"] = confi
            encodings[i]["tamanho"] = size
            encodings[i]["errors"] = fStat["errors"]
            self.wordCount += len(words)
            curWd = 0
            if self.verbose:
                print(
                    f" {i:{4}} | {str(enc):{10}} | {confi:{10}}"
                    f" | {size:{8}}"
                    f" | {os.path.relpath(files[i], self.root)}"
                )
            for wd in words:
                token = self._MakeToken(wd)
                if token == "":
                    continue
                elif token in knownTokens:
                    if token not in fileTokens:
                        invertedIndex[token].append(
                            [i, 1, [curWd]]  # 1 is the #occurances
                        )
                        fileTokens.add(token)
                    else:
                        # Increments #occurances of the last document
                        invertedIndex[token][-1][1] += 1
                        invertedIndex[token][-1][2].append(curWd)
                else:
                    invertedIndex[token] = [[i, 1, [curWd]]]
                    fileTokens.add(token)
                    knownTokens.add(token)
                curWd += 1
        if self.showToken:
            for t in knownTokens:
                print(t)

    def _MakeToken(self, word):
        return word.lower()

    # Returns the encoding information and the words a file contains
    def _ReadFile(self, file):
        fStat = self._GetEncode(file)
        with open(
            file, encoding=fStat["encoding"], errors=fStat["errors"]
        ) as f:
            words = f.read().split()
        generatedWords = []
        for wd in words:
            generatedWords += util.StripPunctuation(wd)
        return fStat, generatedWords

    def _GetEncode(self, filename):
        enc = self.fixedEncode
        if filename in enc.keys():
            return {
                "encoding": enc[filename],
                "confidence": 1,
                "errors": "strict",
            }
        with open(filename, "rb") as f:
            encode = chardet.detect(f.read(MAXSIZE))
            if (
                os.stat(filename).st_size > MAXSIZE
                and encode["encoding"] == "ascii"
            ):
                encode["encoding"] = "utf-8"
                encode["confidence"] = 0.4
                er = "mixed"
            elif encode["confidence"] < 0.63:
                er = "replace"
            else:
                er = "strict"
            encode["errors"] = er
        encode["tamanho"] = os.path.getsize(filename)
        return encode

    def _BuildPositionalIndex(self):
        index = self.index
        positional = np.array([], dtype=int)
        curInd = 0
        for tkIndex in self.index.values():
            for docIndex in tkIndex:
                positional = np.concatenate((positional, docIndex[2]))
                docIndex[2] = curInd
                curInd += docIndex[1]
        self.positionalIndex = positional
