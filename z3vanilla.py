from z3 import *
#import time
#start = time.time()
g = Goal()

#It starts in tsetin variable '1'
#initvar = 1
#auxinitvars = BitVec('auxinitvars', initvar)
vars = []
bitvecsvars = ""

#Input model NFs initialisation
stringvars = ['a', 'b', 'c', 'd']
p = Bool('p')
for modelnamevar in stringvars:
    bitvecsvars+= modelnamevar+' '
vars =  BitVecs(bitvecsvars[:-1], 2)
Pre = BitVec('Pre', 4)
Post = BitVec('Post', 4)
ten = BitVecVal(1, 2)
NumCore = BitVec('NumCore', 2)
#Necessary to get rido of k!0 as the first variable involved (which we want to erase to start with variable 1)
#g.add(auxinitvars == 1) #necessary to get rid

#NFM Constraint
#g.add(ULE(vars[0], vars[1]), UGE(vars[1], vars[0]), vars[0] == 1, UGT(vars[2], vars[3]))
#g.add(p == (vars[0] + ten == 2))
# g.add(Pre >= 0)
# g.add(Pre <= 4)
# g.add(Pre >= 0)
# g.add(Pre <= 4)
# g.add(Pre + Post > 0)
#x = FP('x', FPSort(3, 4))
#g.add(x + 1 < 10)
#g.add(Or(vars[0] == 0,  vars[0] == 1,  vars[0] == 2,  vars[0] == 3))
#g.add(ULT(vars[3], 4), ULE(vars[0] + vars[1] + vars[2], vars[3]))
#g.add(vars[0] * (vars[1] + vars[2]) == vars[3], vars[0] == 1)
#g.add(vars[0] >= vars[1], vars[0] == 1, vars[2] != vars[3], vars[2] == 1)
#g.add(vars[0] + vars[1] == 2, vars[1] == 1)
t = Then('simplify', 'bit-blast', 'tseitin-cnf')
subgoal = t(g)
assert len(subgoal) == 1
#print(subgoal[0])
maxrange = len(subgoal[0])
initvars = 1
for c in range (maxrange):
    aux = str(subgoal[0][c]).replace("Or(", "")
    aux = aux.replace("\n  ", "")
    aux = aux.replace("k!", "")
    aux = aux.replace("Not(", "-")
    aux = aux.replace("))", "")
    aux = aux.replace(")", "")
    aux = aux.replace(",", "")
    ##### UPDATING THE NUMBER OF VARIABLE (VAR_ID) #####
    auxarray = aux.split(' ')
    updatedaux = ''
    for literalvar in auxarray:
        numliteralvar = int(literalvar)
        if numliteralvar < 0:
            updatedaux += str(numliteralvar - initvars) + ' '
        else:
            updatedaux += str(numliteralvar + initvars) + ' '
    print(updatedaux+'0')
print(g)
print(simplify(g[1]))