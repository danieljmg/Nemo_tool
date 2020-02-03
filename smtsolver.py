# import secrets
from z3 import *

def smtsolverexec(file_vars):
    constraints = Then('simplify', 'bit-blast', 'tseitin-cnf', 'smt').solver()
    # s.set(random_seed=secrets.randbelow(5000))
    # s.set(phase_selection=secrets.randbelow(5))

    numbersolutions=0
    while constraints.check() == sat:
        m = constraints.model()
        numbersolutions += 1
        print(numbersolutions)
        print(m)
        newc = "Or("
        for var in file_vars:
            newc += f"{var[0]} != m[{var[0]}], "
        newc = newc[:-2] + ")"
        constraints.add(newc)