# pip install sympy
from sympy.logic.boolalg import to_cnf
from sympy.abc import a, b, c, d, e, f, g, h, i, j, k, l
b = ~(a) &~(f) &~(~((~(k) |~((j |(h |i |~((~(i) |~(h)))) |~((~(j) |~((h |i |~((~(i) |~(h)))))))))))) &(~((~((h |i |j |k)) &~((d |e |f |g)))) |~((l |a |b |c))) &~(b) &~(c) &~(g)
print(to_cnf(b,))
