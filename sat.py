import pycosat
# p cnf 5 3 => 5 vars 3 clauses
# 1 -5 4 0 => x1 or not x5 or x4 or x0
# -1 5 3 4 0
# -3 -4 0
#[['a1 a2', 'a1'], ['-a1', '-a1 -a2']]
#cnf = [[1, 2, 3], [-1, -2], [-1, -3], [-1, -2, -3]]
#cnf = [[-1, -2], [-1, -3], [-1, -2, -3], [1, -2, 3]]

#vars[0] == 0, vars[0] < vars[1]
#cnf = [[-1], [2, -4], [-2], [2, -1], [2, 3], [-1, -4], [3, -4]]
#SOLS: [-1, -2, 3, -4] => a = (2_0,1_0), b = (4_0,3_1)
#hint: a_(k1, k2)
#Q&A: With the equality/constraint we are forcing Z3 to convert it first

#vars[0] < vars[1], vars[0] == 0
cnf = [[4, -2], [-3], [4, -3], [1, 4], [-2, -3], [1, -2], [-4]]
#SOLS: [1, -2, -3, -4] => a = (4_0,3_0), b = (2_0,1_1)
#hint: a_(k3, k4)
#Q&A: It is converting the first constraint first.


#vars[0] < vars[1]
cnf = [[4, -2], [4, -3], [1, 4], [-2, -3], [1, -2]]
#SOLS:

print(pycosat.solve(cnf))
print("Solutions:")
for sol in pycosat.itersolve(cnf):
    print(sol)