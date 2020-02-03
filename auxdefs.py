from z3 import *
def embeed(constraints):
    A = BitVec('A', 5)
    B = BitVec('B', 5)
    C = BitVec('C', 5)
    constraints.add(ULT(A, 16))
    constraints.add(ULT(B, 16))
    constraints.add(ULT(C, 16))
    constraints.add((A + B) == C)