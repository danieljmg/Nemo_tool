'''
    File name: smtsolver.py
    Author: Daniel-Jesus Munoz
    Date created: 30/09/2019
    Python Version: 3.8.
    Description: Z3/SMT solver just for testing purposes
'''

# import secrets

# import secrets
from z3 import *

# set_option(verbose = 10)
# set_option(html_mode=False)
# enable_trace
# set_option(trace = True)
# A + B >= 1 signed needs 3 bits as 1+1 is 2, which is out scope with 2 signed bits. To be right, whether it is singed or unsigned, one addition in a constraint side must increate the number of bits by one, and then one more per two additions, of the variables involved in.
# For each * we must add n times (n == number of consecutive mults) times the largest bit-width for the same reason as the previous (i.e., 2^(m) * 2^(m) * 2^(m) = 2^(3*m)
# (N times * width) - 1 if over one * as we are starting in 0
# We must calculate the greatest increase from both individually ( I think)
constraints = Then('simplify', 'bit-blast', 'tseitin-cnf', 'smt').solver()
A = BitVec('A', 2)
B = BitVec('B', 2)
C = BitVec('C', 2)
D = BitVec('D', 2)
constraints.add(ULE(A, 1))
constraints.add(ULE(B, 1))
constraints.add(ULE(C, 1))
constraints.add(ULE(D, 1))
constraints.add((A + B) == (C + D))
# s.set(random_seed=secrets.randbelow(5000))
# s.set(phase_selection=secrets.randbelow(5))
numbersolutions=0
while constraints.check() == sat:
    m = constraints.model()
    numbersolutions += 1
    print(numbersolutions)
    print(m)
    constraints.add(Or(A != m[A], B != m[B], C != m[C], D != m[D]))