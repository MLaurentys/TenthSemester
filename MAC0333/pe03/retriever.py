import re
import math
from sys import maxsize
import util


class Retriever:
    def __init__(self, prim, sortMethod, amountToShow, aux=None, rem=None):
        self.prim = prim
        self.aux = aux
        self.files = prim[util.LISTFILES].copy()
        self.index = prim[util.INDEX]
        self.positional = prim[util.POSITIONAL]
        print(prim[util.POSITIONAL])
        self.keys = set(self.index.keys())
        self.SortMethod = SORT_METHOD[sortMethod]
        self.amountToShow = amountToShow
        if aux != None:
            self.auxFiles = aux[util.LISTFILES].copy()
            self.auxIndex = aux[util.INDEX]
            self.auxKeys = set(self.auxIndex.keys())
            self.auxPositional = aux[util.POSITIONAL]
            auxFiles = set(aux[util.LISTFILES])
        else:
            self.auxFiles = []
            self.auxIndex = {}
            self.auxKeys = set()
            self.auxPositional = []
            auxFiles = set()
        # Removes 'rem' from prim -> indexMap to be used in queries
        removed = set(rem) if rem != None else set()
        modifiedFiles = auxFiles.intersection(set(self.files))
        toRemove = removed.union(modifiedFiles)
        indMap = self._RemoveFromIndex(toRemove)  # Changes self.files
        self.finalDocumentID = indMap
        self.offsetForAuxiliarIndex = len(self.files)
        print(f"Final list of files: ")
        for f in self.files + self.auxFiles:
            print(f)
        print()

    def _GetIncidence(self, token):
        incidence = []
        if token in self.index.keys():
            incidence = [
                self.finalDocumentID[ind[0]]
                for ind in self.index[token]
                if self.finalDocumentID[ind[0]] != -1
            ]
        if token in self.auxIndex.keys():
            incidence += [
                (ind[0] + self.offsetForAuxiliarIndex)
                for ind in self.auxIndex[token]
            ]
        return incidence

    # Handles SELECT query
    def PrintSelect(self, tokens):
        sets = []
        aKeys = set(self.auxIndex.keys())
        pKeys = set(self.index.keys())
        keys = pKeys.union(aKeys)
        print("Conjugaçao das listas de termos")
        print("  DF  |     Token     | Lista de incidencia")
        for token in tokens:
            if token not in keys:
                print(f" ---- | {token:{11}} | -----")
                sets.append(set())
                break
            incidence = self._GetIncidence(token)
            print(
                f" {len(self.index[token]):{4}} | {token:{13}} | "
                f"{incidence}"
            )
            sets.append(set([ind for ind in incidence]))
        commonFiles = sets[0]
        for st in sets:
            commonFiles = commonFiles.intersection(st)
        commonFiles, results = self.SortMethod(self, tokens, commonFiles)
        print(
            f"Existem {len(commonFiles)} documentos com os {len(tokens)} termos:"
        )
        for doc in commonFiles:
            if doc >= self.offsetForAuxiliarIndex:
                print(
                    f"{doc}: {results[doc]} "
                    f"{self.auxFiles[doc - self.offsetForAuxiliarIndex]}"
                )
            else:
                print(f"{doc}: {results[doc]} {self.files[doc]}")

    def PrintTopo(self, num, match, negMatch):
        keys = list(self.keys.union(self.auxKeys))
        keys = self._SortMethodTopo(keys)
        if match is not None:
            regex = re.compile(match)
            keys = [k for k in keys if regex.match(k)]
        if negMatch is not None:
            regex = re.compile(negMatch)
            keys = [k for k in keys if not regex.match(k)]
        print(f"{len(keys)} tokens matched regex restrictions")
        print(" DF |    Token    | Lista de incidencia")
        for i in range(len(keys) - 1, len(keys) - num - 1, -1):
            print(
                f" {len(self.index[keys[i]]):{2}} | {keys[i]:{11}} | "
                f"{self._GetIncidence(keys[i])}"
            )
        print()

    def _SortMethodTopo(self, keys):
        def CompareValue(item):
            df = len(self.auxIndex[item]) if item in self.auxKeys else 0
            if item in self.keys:
                for doc in self.index[item]:
                    if self.finalDocumentID[doc[0]] != -1:
                        df += 1
            return df

        def CompareValue2(item):
            return str(item)

        it = sorted(
            sorted(keys, key=CompareValue2, reverse=True),
            key=CompareValue,
        )
        return it

    def _SortMethod0(self, docID, tokens, commonFiles):
        return commonFiles

    def _GetTf(self, docID, tokens):
        tf = 0
        for token in tokens:
            i = 0
            while self.finalDocumentID[self.index[token][i][0]] != docID:
                i += 1
            tf += self.index[token][i][1]
        return 1 + math.log10(tf)

    def _GetTfAux(self, docID, tokens):
        docID -= self.offsetForAuxiliarIndex
        tf = 0
        for token in tokens:
            i = 0
            while self.auxIndex[token][i][0] != docID:
                i += 1
            tf += self.auxIndex[token][i][1]
        return 1 + math.log10(tf)

    def _SortMethod1(self, tokens, commonFiles):
        def CompareValue(docID):
            df = math.log10(float(len(self.files)) / float(len(commonFiles)))
            tf = (
                self._GetTf(docID, tokens)
                if docID < self.offsetForAuxiliarIndex
                else self._GetTfAux(docID, tokens)
            )
            results[docID] = tf * df
            return tf * df

        results = {}
        return sorted(commonFiles, key=CompareValue, reverse=True), results

    def _SortMethod2(self, tokens, commonFiles):
        def CompareValue(docID):
            tot = len(self.prim[util.LISTFILES])
            if self.aux != None:
                tot += len(self.aux[util.LISTFILES])
            df = math.log10(float(tot) / float(len(commonFiles)))
            tf = (
                self._GetTf(docID, tokens)
                if docID < self.offsetForAuxiliarIndex
                else self._GetTfAux(docID, tokens)
            )
            results[docID] = tf * df
            return tf * df

        results = {}
        return sorted(commonFiles, key=CompareValue, reverse=True), results

    def _SortMethod3(self, tokens, commonFiles):
        pass

    def _GatherListOfPositions(self, docID, tokens):
        index = self.index
        positions = []
        print(self.positional)
        for token in tokens:
            i = 0
            while self.finalDocumentID[index[token][i][0]] != docID:
                i += 1
            numTerms = index[token][i][1]
            startPos = index[token][i][2]
            positions += self.positional[startPos:numTerms]
        return positions

    def _GatherListOfPositionsAux(self, docID, tokens):
        index = self.auxIndex
        docID -= self.offsetForAuxiliarIndex
        positions = []
        print(self.auxPositional)
        for token in tokens:
            i = 0
            while index[token][i][0] != docID:
                i += 1
            numTerms = index[token][i][1]
            startPos = index[token][i][2]
            positions += self.auxPositional[startPos:numTerms]
        return positions

    def _SortMethod4(self, tokens, commonFiles):
        def CompareValue(docID):
            positions = (
                self._GatherListOfPositions(docID, tokens)
                if docID < self.offsetForAuxiliarIndex
                else self._GatherListOfPositionsAux(docID, tokens)
            )
            results[docID] = util.GetSmallestInterval(positions)
            return len(results[docID])

        results = {}
        return sorted(commonFiles, key=CompareValue), results

    def _RemoveFromIndex(self, setOfFilesToRemove):
        toRem = []
        # Maps initial file ID to final ID
        indMap = {i: i for i in range(len(self.files))}
        offset = 0
        for i in range(len(self.files)):
            if self.files[i] in setOfFilesToRemove:
                toRem.append(i)
                indMap[i] = -1  # Indicates that file was removed
                offset -= 1
            else:
                indMap[i] += offset
        for i in range(len(toRem) - 1, -1, -1):
            self.files.pop(toRem[i])

        return indMap


SORT_METHOD = [
    Retriever._SortMethod0,
    Retriever._SortMethod1,
    Retriever._SortMethod2,
    Retriever._SortMethod3,
    Retriever._SortMethod4,
]
