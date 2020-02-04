from z3 import *
from optimisedparsing import readNFM
from median import calculatemedian
import re
# set_option(verbose = 10)
# set_option(html_mode=False)
# set_option(trace = True)
# traces = ["tseitin_cnf_bug", "tseitin_cnf", "simplify", "before_search", "after_search", "asserted_formulas", "bv", "resolve_conflict", "set_conflict", "arith", "rewriter"]
# for tr in traces:
#    enable_trace(tr)
import time
start = time.time()

z3flag = True
if z3flag:

    modelname = "smtsolutions"

    from smtsolver import main
    main(modelname, start)

else:
    modelname = "transformedmodel"
    f = open(f"{modelname}.dimacs", "w")

    booleanmodelname = ""  # basemodel.dimacs"

    constraints = Goal()

    ##### Input model NFs initialisation #####
    file_vars = []
    file_cts = []
    filepath = 'transformingmodel.txt'
    ##### Parse, adjust and optimise NFM #####
    (file_vars, file_cts) = readNFM(filepath, file_vars, file_cts)
    print(f'Defined variables (Name, Adjusted_width, Type) = {file_vars}')
    print(f'Adjusted constraints = {file_cts}')

    auxf = open("auxdefs.py", "w+")
    auxf.write("from z3 import *\n")
    auxf.write("def embeed(constraints):")
    ##### Define NFM variables in Z3py format #####
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
    auxf.close()
    from auxdefs import embeed

    embeed(constraints)

    ##### constraints == Constraints array || subgoal[0] == CNF PF #####
    # t = WithParams(Then('simplify', 'bit-blast', 'tseitin-cnf'), distributivity=False)
    p = ParamsRef()
    # params_to_false = ["elim_ite", "flat", "bit2bool", "algebraic_number_evaluator", "distributivity",  "common_patterns", "common_patterns", "ite_chaing", "ite_extra", "elim_and", "blast_distinct", "elim_sign_ext", "hi_div0", "ignore_patterns_on_ground_qbody", "push_to_real"]

    # params_to_false = ["elim_ite", "flat", "bit2bool", "algebraic_number_evaluator", "elim_and", "blast_distinct", "elim_sign_ext", "hi_div0", "ignore_patterns_on_ground_qbody", "push_to_real"]
    # for param in params_to_false:
    #    p.set(param, False)

    # p.set("distributivity_blowup", 0)

    t = WithParams(Then('simplify', 'bit-blast', 'tseitin-cnf'), p)
    # t = WithParams(Then('simplify', 'bit-blast'), p)
    # print(t.__setattr__("distributivity", False))
    subgoal = t(constraints)
    # (subgoal[0])
    assert len(subgoal) == 1
    # auxbb = open("pbb.txt","w+")
    # for pbb in subgoal[0]:
    # auxbb.write(str(pbb))
    # auxbb.write(" and\n")
    # auxbb.close()
    # print(subgoal[0])

    ##### Traverse each clause of the first subgoal #####
    maxrange = len(subgoal[0])

    bitvarsmap = []
    ##### If the model contain constraints ... #####
    for constraint in constraints:
        # print(constraint)
        ##### Remove parenthesis #####
        complexstrconstraint = str(constraint).replace('\n  ', '')
        complexstrconstraint = complexstrconstraint.replace('Not(', '')
        complexstrconstraint = complexstrconstraint.replace('(', '')
        complexstrconstraint = complexstrconstraint.replace(')', '')
        if 'Implies' == complexstrconstraint[0:7]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[7:].split(', ')
        elif 'UDiv' == complexstrconstraint[0:4]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[7:].split(', ')
        elif 'URem' == complexstrconstraint[0:4]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[7:].split(', ')
        elif 'Or' == complexstrconstraint[0:2]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[2:].split(', ')
        elif 'And' == complexstrconstraint[0:3]:
            ##### Sequential Order #####
            found_complex_ops = complexstrconstraint[2:].split(', ')
        else:
            found_complex_ops = [complexstrconstraint]

        for strconstraint in found_complex_ops:
            if 'ULT' in strconstraint or 'UGE' in strconstraint:
                ##### Reverse Order #####
                found_ops = strconstraint[3:].split(', ')[::-1]
            elif " < " in strconstraint:
                ##### Reverse Order #####
                found_ops = strconstraint.split(' < ')[::-1]
            elif " >= " in strconstraint:
                ##### Reverse Order #####
                found_ops = strconstraint.split(' >= ')[::-1]
            elif " <= " in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint.split(' <= ')
            elif " > " in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint.split(' > ')
            elif " == " in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint.split(' == ')
            elif " != " in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint.split(' !=')
            elif 'ULE' in strconstraint or 'UGT' in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint[3:].split(', ')
            elif 'UDiv' in strconstraint or 'URem' in strconstraint:
                ##### Sequential Order #####
                found_ops = strconstraint[4:].split(', ')
            else:
                found_ops = [strconstraint]
            equation_vars = re.split(' \+ | - |\*|/|%', found_ops[0])
            if len(found_ops) > 1:
                equation_vars += re.split(' \+ | - |\*|/|%', found_ops[1])
            for found_var in equation_vars:
                if not found_var.isnumeric() and found_var.replace(" ", "").replace("And", "").replace("Or",
                                                                                                       "").replace(
                    "UDiv", "").replace("URem", "") not in bitvarsmap: bitvarsmap.append(found_var.replace(" ", ""))

    ##### Initialise var and clauses counters, and write variables of the second model depending on its existence #####
    initconstraints = 0
    if (booleanmodelname):
        with open(booleanmodelname) as input_file:
            input_file_content = input_file.read().splitlines()
            for input_line in input_file_content:
                if 'c ' == input_line[0:2]:
                    f.write(input_line)
                    f.write("\n")
                elif 'p cnf ' == input_line[0:6]:
                    vars_and_constraints = input_line[6:].split(' ')
                    initvars = int(vars_and_constraints[0]) + 1
                    initconstraints = int(vars_and_constraints[1])
    else:
        initvars = 1

    ##### Identify true variables #####
    varcounter = initvars
    ##### Mapping of Boolean vars and their ids #####
    booleanvarsids = []
    # print(bitvarsmap)
    for bitvar in bitvarsmap:
        # si es booleano 1, si no el bit width
        ##### Look for type and width #####
        for auxvardefs in file_vars:
            if auxvardefs[0] == bitvar:
                auxvardef = auxvardefs
        if auxvardef[2] != 'boolean':
            for bit in range(1, auxvardef[1] + 1):
                # print(f"c {varcounter} {bitvar}_{bit}")
                f.write(f"c {varcounter} {bitvar}_{bit}")
                f.write("\n")
                varcounter += 1

    # numvars = len(z3util.get_vars(subgoal.as_expr())) - num_predifined_booleans
    aux_vars_z3 = z3util.get_vars(subgoal.as_expr())
    num_vars = 0
    for aux_counter in aux_vars_z3:
        if '!' in str(aux_counter):
            current_aux = int(str(aux_counter).split('!')[1]) + 1
            if num_vars < current_aux:
                num_vars = int(current_aux)

    # print(num_vars)
    ##### Followed by Tseitin variables #####
    tseitincounter = 1
    if varcounter < (num_vars + initvars):
        for totalvarsid in range(varcounter, num_vars + initvars):
            # print(f"c {auxvarsid} Tseitin_Variable_{tseitincounter}")
            f.write(f"c {totalvarsid} Tseitin_Variable_{tseitincounter}")
            f.write("\n")
            tseitincounter += 1
    else:
        totalvarsid = varcounter - 1

    ### Boolean vars at the end (if were not predefined in a base model ###
    for bitvar in bitvarsmap:
        # si es booleano 1, si no el bit width
        ##### Look for type and width #####
        for auxvardefs in file_vars:
            if auxvardefs[0] == bitvar:
                auxvardef = auxvardefs
        if auxvardef[2] == 'boolean':
            if auxvardef[1] == 0:
                totalvarsid += 1
                f.write(f"c {totalvarsid} {bitvar} boolean")
                f.write("\n")
                booleanvarsids.append([bitvar, totalvarsid])
            else:
                booleanvarsids.append([bitvar, auxvardef[1]])

    ##### Transform Z3 output to DIMACS CNF NFM #####
    # print(f"p cnf {numvars} {maxrange}")
    f.write(f"p cnf {totalvarsid} {maxrange + initconstraints}")
    f.write("\n")

    ##### Add clauses of the second model if needed #####
    if (booleanmodelname):
        with open(booleanmodelname) as input_file:
            input_file_content = input_file.read().splitlines()
            for input_line in input_file_content:
                if input_line[0:4] != "def " and input_line[0:2] != "c " and input_line[0:2] != "p ":
                    f.write(input_line)
                    f.write("\n")

    # print(booleanvarsids)
    for c in range(maxrange):
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
            if (literalvar == '-0'):
                updatedaux += str(f"-{initvars}") + ' '
            else:

                if literalvar.lstrip("-").isnumeric():
                    numliteralvar = int(literalvar)
                    if numliteralvar < 0:
                        updatedaux += str(numliteralvar - initvars) + ' '
                    else:
                        updatedaux += str(numliteralvar + initvars) + ' '
                else:
                    updatedaux += str(f"{literalvar}") + ' '
        ##### Replace booleans by their ids #####
        for bv in booleanvarsids:
            updatedaux = updatedaux.replace(bv[0], str(bv[1]))
        # print(updatedaux+'0')
        f.write(updatedaux + '0')
        if (c < maxrange - 1): f.write("\n")
    f.close()
    end = time.time() - start  # - 0.05
    print(f"Transformation time: {str(end).replace('.', ',')} seconds")
    calculatemedian(filepath)