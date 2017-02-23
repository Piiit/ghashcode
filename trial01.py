# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 10:55:15 2017

@author: pemoser and danila
"""

import dlh
import collections
import matplotlib.pyplot as plt
import numpy as np

# Named tuples are immutable
Dimension = collections.namedtuple('Dimension', 'row, col')
Slice = collections.namedtuple('Slice', 'row1, col1, row2, col2, mush, toma')

class Piece:
    def __init__(self, row, col, type, slices):
        self.row = row
        self.col = col
        self.type = type
        self.slices = slices
        self.mark = 0


class Pizza:
    def __init__(self, fn):
        # First Line = R (rows), C (cols), L (min. ingredient), H (max. splice)
        file = open(fn, "r")
        (R, C, L, H) = file.readline().split(" ")
        (self.R, self.C, self.L, self.H) = (int(R), int(C), int(L), int(H))

        # 2*L <= size <= H
        self.minSize = 2*self.L
        self.maxSize = self.H

        self.maxDimWidth = 0
        self.maxDimHeight = 0

        # Pizza data
        self.matrix = []
        row = 0
        for l in file.readlines():
            line = []
            col = 0
            for ll in l[:-1]:
                p = Piece(row, col, ll, [])
                line.append(p)
                col += 1
            self.matrix.append(line)
            row += 1

        # Calculate possible dimensions of slices
        self.dims = []
        for j in range(self.minSize, self.maxSize + 1):
            divs = []
            for x in dlh.divisors(j):
                divs.append(x)

            i = len(divs) - 1
            for divisor in divs:
                if i < (len(divs)/2) - 1:
                    break
                if divisor <= self.C and divs[i] <= self.R:
                    self.dims.append(Dimension(divs[i], divisor))
                    self.maxDimWidth = max(self.maxDimWidth, divisor)
                    self.maxDimHeight = max(self.maxDimHeight, divs[i])
                i -= 1

        # Start from biggest slice type...
        self.dims = sorted(self.dims, key=lambda x: x[0] * x[1], reverse=True)

        self.pickNo = 0


    # Caller must check for boundaries
    def findSlice(self, dim, col, row):
        cM = 0
        for r in self.matrix[row:row + dim.row]:
            for c in r[col:col + dim.col]:
                if c.type == 'M':
                    cM += 1

        cT = dim.row * dim.col - cM
        if cM < self.L or cT < self.L:
            return None

        sl = Slice(row, col, row + dim.row - 1, col + dim.col - 1, cM, cT)

        # Mark pieces with this slice
        for r in range(row, row + dim.row):
            for c in range(col, col + dim.col):
                self.matrix[r][c].slices.append(sl)


    # Attempt 1: Exhaustive Search - Find valid slices (overlapping)
    def findAllSlices(self):
        for dim in self.dims:
            for row in range(self.R - dim.row + 1):
                for col in range(self.C - dim.col + 1):
                    self.findSlice(dim, col, row)


    def pickSlice(self, sl):

        self.pickNo += 5

        # Delete all slices within the picked slice's boundaries
        for r in range(sl.row1, sl.row2 + 1):
            for c in range(sl.col1, sl.col2 + 1):
                self.matrix[r][c].slices = []
                if self.matrix[r][c].mark != 0:
                    raise("ERROR: ", r,c, sl, self.matrix[r][c].slices)
                self.matrix[r][c].mark += self.pickNo

        # Delete some slices that overlap with the current slice
        # outside from pieces outside this piece's boundaries...
        rowFrom = max(0, sl.row1 - self.maxDimHeight + 1)
        rowTo = min(self.R - 1, sl.row2 + self.maxDimHeight - 1)

        colFrom = max(0, sl.col1 - self.maxDimWidth + 1)
        colTo = min(self.C - 1, sl.col2 + self.maxDimWidth - 1)

        for r in range(rowFrom, rowTo + 1):
            for c in range(colFrom, colTo + 1):
                slices = []
                for s in self.matrix[r][c].slices:
                    if (s.row1 > sl.row2 or s.row2 < sl.row1 or s.col1 > sl.col2 or s.col2 < sl.col1):
                        slices.append(s)
                self.matrix[r][c].slices = slices

        return sl


    def print(self):
        for r in self.matrix:
            for c in r:
                print(c.type, end="")
            print()

    def printSlices(self, row, col):
        print(self.matrix[row][col].slices)

    def printSlice(sl):
        print ("%s %s %s %s" % (sl.row1, sl.col1, sl.row2, sl.col2))


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
inputfile = "small.in"
pizza = Pizza(inputfile)
#pizza.print()
pizza.findAllSlices()
print("Slices found...")

import datetime

now = datetime.datetime.now()

count = 0
result = []

# Naive solution, pick always the first available slice inside a piece...
for row in range(pizza.R):
    for col in range(pizza.C):
        #print(row, col)
        if len(pizza.matrix[row][col].slices) > 0:
            sl = pizza.pickSlice(pizza.matrix[row][col].slices[0])
            #pizza.print()
            #print()
            result.append(sl)
            count += 1
            if count % 100 == 0:
                print("Count = ", count)


print("DONE: count = ", count)

print("Writing result to file")
with open("result-%s-%s.txt" % (inputfile, now.isoformat()), "a") as resultfile:
    resultfile.write("%d\n" % count)
    for sl in result:
        resultfile.write("%s %s %s %s\n" % (sl.row1, sl.col1, sl.row2, sl.col2))
print("DONE")

def draw(pizza):
    aa = np.zeros((pizza.R, pizza.C))
    cc = 0
    for row in range(pizza.R):
        for col in range(pizza.C):
            aa[row, col] = pizza.matrix[row][col].mark
            if pizza.matrix[row][col].mark != 0:
                cc += 1

    print("Score: ", cc)
    return aa

print("WHITE means uncovered")
plt.matshow(draw(pizza), cmap=plt.cm.Greys)


