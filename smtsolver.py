from optimisedparsing import readNFM
import time
def main(modelname, start):
    f = open(f"{modelname}.txt", "w")

    ##### Input model NFs initialisation #####
    file_vars = []
    file_cts = []
    filepath = 'transformingmodel.txt'
    ##### Parse, adjust and optimise NFM #####
    (file_vars, file_cts) = readNFM(filepath, file_vars, file_cts)
    print(f'Defined variables (Name, Adjusted_width, Type) = {file_vars}')
    print(f'Adjusted constraints = {file_cts}')

    auxf = open("auxsmt.py", "w+")
    auxf.write("from z3 import *\n")
    auxf.write("def smtsolverexec():\n")
    auxf.write("    constraints = Then('simplify', 'bit-blast', 'tseitin-cnf', 'smt').solver()")

    for file_var in file_vars:
        if file_var[2] == 'boolean':
            auxf.write(f"\n    {file_var[0]} = Bool('{file_var[0]}')")
        elif 'constant_' in file_var[2]:
            constant_value = str(file_var[2]).split('_')[1]
            auxf.write(f"\n    {file_var[0]} = BitVecVal({constant_value}, {file_var[1]})")
        else:
            auxf.write(f"\n    {file_var[0]} = BitVec('{file_var[0]}', {file_var[1]})")

    ##### Define NFM constraints in Z3py format #####
    for file_ct in file_cts:
        auxf.write(f"\n    constraints.add({file_ct})")
    ##### Close the file and execute the dinamically generated code #####

    auxf.write(f"\n    numbersolutions = 0")
    auxf.write(f"\n    while constraints.check() == sat:")
    auxf.write(f"\n        m = constraints.model()")
    auxf.write(f"\n        numbersolutions += 1")
    auxf.write(f"\n        print('Solution number: '+str(numbersolutions))")
    auxf.write(f"\n        print(m)")
    auxf.write(f"\n        constraints.add(Or(A != m[A], B != m[B], C != m[C]))")

    auxf.close()

    auxf.close()
    from auxsmt import smtsolverexec
    smtsolverexec()

    end = time.time() - start  # - 0.05
    print(f"\nTransformation and SMT solver time: {str(end).replace('.', ',')} seconds")