import util
import indexer
import pickle
import time


class MIRA(indexer.MIR):
    def __init__(self, parentFolder, fixedEncodeFilename, verbose, showToken):
        super().__init__(parentFolder, fixedEncodeFilename, verbose, showToken)
        princ = util.LoadData(parentFolder, True)
        if princ is None:
            print("Indexamento principal nao encontrado. Abortando...")
            exit(1)
        self.mainFiles = princ[util.LISTFILES]
        encs = princ[util.ENCODINGS]
        self.mainFilesModified = [
            encs[i]["modificado"] for i in range(len(self.mainFiles))
        ]

    def Build(self):
        self._ReadEncodeFile()
        self._GetFiles()
        self._FixFiles()
        self._CreateIndex()
        self._BuildPositionalIndex()

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
        for i in range(len(mf)):
            if mf[i] in self.keptFiles:
                timeIndex[mf[i]] = self.mainFilesModified[i]
        for i in range(len(f)):
            if f[i] in self.keptFiles:
                timeFiles[f[i]] = self.encodings[i]["modificado"]
        for file in self.keptFiles:
            if timeIndex[file] != timeFiles[file]:
                modified.append(file)
        self.modified = set(modified)
        print(
            f"De {len(mf)} para {len(f)}, foram acrescentados {len(self.newFiles)}"
            f" arquivos novos e {len(self.deletedFiles)} removidos."
        )
        print(
            f"Permaneceram {len(self.keptFiles)}, dos quais {len(self.modified)}"
            f" foram modificados."
        )
        self.files = sorted(list(self.modified.union(self.newFiles)))

    def Serialize(self):
        open(self.root + "/mira.pickle", "w").close()  # Erases old content
        open(self.root + "/mira.rem", "w").close()  # Erases old content
        with open(self.root + "/mira.rem", "wb") as f:
            pickle.dump(list(self.deletedFiles), f)
        with open(self.root + "/mira.pickle", "wb") as f:
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
            f"tokens. Informations saved on mira.pickle and mira.rem to load "
            f"via pickle."
        )
