import re

import util


class Retriever:
    def __init__(self, prim, aux=None, rem=None):
        self.files = prim[util.LISTFILES]
        self.index = prim[util.INDEX]
        self.enc = prim[util.ENCODINGS]
        self.keys = set(self.index.keys())
        if aux != None:
            self.auxFiles = aux[util.LISTFILES]
            self.auxIndex = aux[util.INDEX]
            self.auxKeys = set(self.auxIndex.keys())
            auxFiles = set(aux[util.LISTFILES])
        else:
            self.auxFiles = []
            self.auxIndex = {}
            self.auxKeys = set()
            auxFiles = set()
        # Removes 'rem' from prim -> indexMap to be used in queries
        removed = set(rem) if rem != None else set()
        modifiedFiles = auxFiles.intersection(set(self.files))
        toRemove = removed.union(modifiedFiles)
        indMap = self._RemoveFromIndex(toRemove)
        self.finalDocumentID = indMap
        self.offsetForAuxiliarIndex = len(self.files)
        print(f"Final list of files: ")
        for f in self.files + self.auxFiles:
            print(f)
        print()

    # Handles SELECT query
    def PrintSelect(self, tokens):
        sets = []
        aKeys = set(self.auxIndex.keys())
        pKeys = set(self.index.keys())
        keys = pKeys.union(aKeys)
        print("Conjugaçao das listas de termos")
        print("  DF  |    Token    | Lista de incidencia")
        for token in tokens:
            if token not in keys:
                print(f" ---- | {token:{11}} | -----")
                sets.append(set())
            else:
                pInc = []
                aInc = []
                if token in pKeys:
                    pInc = [
                        self.finalDocumentID[ind[0]]
                        for ind in self.index[token]
                        if self.finalDocumentID[ind[0]] != -1
                    ]
                if token in aKeys:
                    aInc = [
                        ind[0] + self.offsetForAuxiliarIndex
                        for ind in self.auxIndex[token]
                    ]
                print(
                    f" {len(self.index[token]):{4}} | {token:{11}} | "
                    f"{pInc + aInc} | {self.index[token]}"
                )
                sets.append(set([ind for ind in pInc + aInc]))
        print(sets)
        res = sets[0]
        for st in sets:
            res = res.intersection(st)
        print(f"Existem {len(res)} documentos com os {len(tokens)} termos:")
        for doc in res:
            if doc >= self.offsetForAuxiliarIndex:
                print(
                    f"{doc}: {self.auxFiles[doc - self.offsetForAuxiliarIndex]}"
                )
            else:
                print(f"{doc}: {self.files[doc]}")

    def PrintTopo(self, num, match, negMatch):
        keys = list(self.keys.union(self.auxKeys))
        keys = sorted(
            sorted(keys, key=self._CompareValue2, reverse=True),
            key=self._CompareValue,
        )
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
                f"{self._GetIncidence(keys, i)}"
            )
        print()

    def _CompareValue(self, item):
        df = len(self.auxIndex[item]) if item in self.auxKeys else 0
        if item in self.keys:
            for doc in self.index[item]:
                if self.finalDocumentID[doc[0]] != -1:
                    df += 1
        return df

    def _CompareValue2(self, item):
        return str(item)

    def _GetIncidence(self, keys, i):
        incidence = [
            self.finalDocumentID[ind[0]]
            for ind in self.index[keys[i]]
            if self.finalDocumentID[ind[0]] != -1
        ]
        incidence += [
            (ind[0] + self.offsetForAuxiliarIndex)
            for ind in self.auxIndex[keys[i]]
        ]
        return incidence

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