from z3 import *
x = BitVec('x', 16)
y = BitVec('y', 16)
z = BitVec('z', 16)

g = Goal()

bitmap = {}
for i in range(16):
    bitmap[(x,i)] = Bool('x'+str(i))
    mask = BitVecSort(16).cast(math.pow(2,i))
    g.add(bitmap[(x,i)] == ((x & mask) == mask))

g.add(x == y, z > If(x < 0, x, -x))

print(g)

# t is a tactic that reduces a Bit-vector problem into propositional CNF
t = Then('simplify', 'bit-blast', 'tseitin-cnf')
subgoal = t(g)
assert len(subgoal) == 1
# Traverse each clause of the first subgoal
for c in subgoal[0]:
    print(c)

solve(g)