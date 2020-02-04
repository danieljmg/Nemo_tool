from z3 import *
def embeed(constraints):
    A = BitVec('A', 3)
    B = BitVec('B', 3)
    C = BitVec('C', 3)
    constraints.add(ULT(A, 4))
    constraints.add(ULT(B, 4))
    constraints.add(ULT(C, 4))
    constraints.add((A + B) == C)