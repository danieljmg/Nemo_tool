'''
    File name: x.py
    Author: Daniel-Jesus Munoz
    Date created: 30/09/2019
    Python Version: 3.8.
    Description: Mainfile of the tool that transform Numerical Feature Models into a CNF DIMACS file by means of Bit-Blasting (Nemo)
'''

from z3 import *
from optimisedparsing import readNFM
from mode import calculatemedian
import re

##### Debugging details begin #####
# set_option(verbose = 10)
# set_option(html_mode=False)
# set_option(trace = True)
# traces = ["tseitin_cnf_bug", "tseitin_cnf", "simplify", "before_search", "after_search", "asserted_formulas", "bv", "resolve_conflict", "set_conflict", "arith", "rewriter"]
# for tr in traces:
#    enable_trace(tr)
##### Debugging details end #####
#set_option(bounded = True, max_indent = 1000000000, auto_config = False, max_lines=100000000000000, max_width=10000000000000, dump_models = True, debug_ref_count = True, memory_high_watermark = 100000000000000, memory_max_alloc_count = 100000000000000000, memory_max_size = 10000000000000000, rlimit = 1000000000000, stats = True)
#set_pp_option(max_lines = 100000000000, max_width = 10000000, bounded = False, max_indent = 100000)
set_option(max_depth = 10000000000)
# https://github.com/Z3Prover/z3/blob/5a1003f6ed10fc65a1cbcd2554f183714c413c7c/src/api/python/z3/z3printer.py#L453

import time
start = time.time()

# z3flag = input("Do you want to run the model in the Z3 SMT solver (y)?: ")
# if z3flag != 'y': dimacsflag = input("Do you want to transform the model into DIMACS (y)?: ")
z3flag = 'n'
dimacsflag = 'y'

if z3flag == 'y':

    from smtsolver import main
    main(start)

elif dimacsflag == 'y':
    #filepath = input("Which is the model .txt to transform?: ")
    filepath = 'transformingmodel.txt'

    # booleanmodelname = input("If you are extendiyng a DIMACS model, please write its name, BLANK otherwise: ")
    # if (booleanmodelname): booleanmodelname = "" + ".dimacs"  # basemodel.dimacs"
    booleanmodelname = ""

    ##### Initialise resulting file and the Z3 constraints variable #####
    modelname = "transformedmodel"
    f = open(f"{modelname}.dimacs", "w")
    constraints = Goal()

    ##### Input model NFs initialisation #####
    file_vars = []
    file_cts = []


    ##### Parse, adjust and optimise NFM #####
    (file_vars, file_cts) = readNFM(filepath, file_vars, file_cts)
    print(f'Defined features (Name, Adjusted_width, Type) = {file_vars}')
    print(f'Adjusted constraints = {file_cts}')

    ##### Start generating the dynamic Z3 python module #####
    auxf = open("auxdefs.py", "w+")
    auxf.write("from z3 import *\n")
    auxf.write("def embeed(constraints):")
    ##### Dynamically define NFM variables in Z3py format #####
    for file_var in file_vars:
        if file_var[2] == 'boolean':
            auxf.write(f"\n    {file_var[0]} = Bool('{file_var[0]}')")
        elif 'constant_' in file_var[2]:
            constant_value = str(file_var[2]).split('_')[1]
            auxf.write(f"\n    {file_var[0]} = BitVecVal({constant_value}, {file_var[1]})")
        else:
            auxf.write(f"\n    {file_var[0]} = BitVec('{file_var[0]}', {file_var[1]})")

    ##### Dynamically define NFM constraints in Z3py format #####
    for file_ct in file_cts:
        auxf.write(f"\n    constraints.add({file_ct})")
    ##### Close the file and execute the dinamically generated code #####
    auxf.close()
    from auxdefs import embeed
    embeed(constraints)

    ##### Debugging details begin #####
    #p = ParamsRef()
    # params_to_false = ["elim_ite", "flat", "bit2bool", "algebraic_number_evaluator", "distributivity",  "common_patterns", "common_patterns", "ite_chaing", "ite_extra", "elim_and", "blast_distinct", "elim_sign_ext", "hi_div0", "ignore_patterns_on_ground_qbody", "push_to_real"]
    # params_to_false = ["elim_ite", "flat", "bit2bool", "algebraic_number_evaluator", "elim_and", "blast_distinct", "elim_sign_ext", "hi_div0", "ignore_patterns_on_ground_qbody", "push_to_real"]
    # for param in params_to_false:
    #    p.set(param, False)
    # p.set("distributivity_blowup", 0)

    # t = WithParams(Then('simplify', 'bit-blast', 'tseitin-cnf'), distributivity=False)
    # t = WithParams(Then('simplify', 'bit-blast', 'tseitin-cnf'), p)
    # t = WithParams(Then('simplify', 'bit-blast'), p)
    # print(t.__setattr__("distributivity", False))
    ##### Debugging details end #####

    ##### Tactics definition and assertion test #####
    p = ParamsRef()
    t = WithParams(Then('simplify', 'bit-blast'), p)
    # t = WithParams(Then('simplify', 'bit-blast', 'tseitin-cnf'), p)
    subgoal = t(constraints)
    assert len(subgoal) == 1

    ##### Debugging details begin #####
    auxbb = open("pbb.txt","w+")
    for pbb in subgoal[0]:
        auxbb.write(str(pbb))
        auxbb.write(" and\n")
    auxbb.close()
    from cnftrans import main
    main(subgoal[0])

    #print(subgoal[0])

    ##### Debugging details end #####

    ##### subgoal[0] is the CNF PF #####
    maxrange = len(subgoal[0])

    ##### Initialise array to register the order in which the Features and bits are converted, in order to identify them later in the DIMACS file 'c' section #####
    bitvarsmap = []

    ##### Traverse each clause: If the model contain constraints ... #####
    for constraint in constraints:
        # print(constraint)
        ##### Remove parenthesis and negations as they are not necessary to calculate the order #####
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
            ##### Not a nested group of constraints => Nothing to split #####
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
                ##### Not a nested group of constraints => Nothing to split #####
                found_ops = [strconstraint]

            ##### Group of arithmetic operations in sequential Order #####
            equation_vars = re.split(' \+ | - |\*|/|%', found_ops[0])
            if len(found_ops) > 1:
                ##### Register variables temporary #####
                equation_vars += re.split(' \+ | - |\*|/|%', found_ops[1])

            ##### Preventing duplicated variables #####
            for found_var in equation_vars:
                if not found_var.isnumeric() and found_var.replace(" ", "").replace("And", "").replace("Or", "").replace("UDiv", "").replace("URem", "") not in bitvarsmap: bitvarsmap.append(found_var.replace(" ", "").replace(" ", "").replace("And", "").replace("Or", "").replace("UDiv", "").replace("URem", ""))

    ##### Initialise var and clauses counters by means of 'c' identification, and copy the variables of the extending model (if exists) #####
    if (booleanmodelname):
        with open(booleanmodelname) as input_file:
            input_file_content = input_file.read().splitlines()
            for input_line in input_file_content:
                if 'c ' == input_line[0:2]:
                    f.write(input_line)
                    f.write("\n")
                elif 'p cnf ' == input_line[0:6]:
                    ##### New variables and constraints start to count from the extending count #####
                    vars_and_constraints = input_line[6:].split(' ')
                    initvars = int(vars_and_constraints[0]) + 1
                    initconstraints = int(vars_and_constraints[1])
                    break
    else:
        ##### Or we rather part from the first ids #####
        initvars = 1
        initconstraints = 0

    ##### Initialise the variables counter #####
    varcounter = initvars
    ##### Mapping of Boolean vars and their ids #####
    booleanvarsids = []
    # print(bitvarsmap)
    ##### Identify true variables #####
    for bitvar in bitvarsmap:
        ##### Look for type and width #####
        for auxvardefs in file_vars:
            ##### Matching current with declared variables #####
            if auxvardefs[0] == bitvar:
                auxvardef = auxvardefs
        if auxvardef[2] != 'boolean':
            ##### NF => #Bits IDs, Boolean Fs are treated later on #####
            for bit in range(1, auxvardef[1] + 1):
                # print(f"c {varcounter} {bitvar}_{bit}")
                f.write(f"c {varcounter} {bitvar}_{bit}")
                f.write("\n")
                varcounter += 1

    ##### To calculate Tseitin Variables, we parse the transformation looking for the largest feature ID #####
    aux_vars_z3 = z3util.get_vars(subgoal.as_expr())
    num_vars = 0
    for aux_counter in aux_vars_z3:
        if '!' in str(aux_counter):
            current_aux = int(str(aux_counter).split('!')[1]) + 1
            if num_vars < current_aux:
                num_vars = int(current_aux)

    # print(num_vars)
    ##### We now identify Tseitin variables in the 'c' section of the DIMACS file #####
    tseitincounter = 1
    if varcounter < (num_vars + initvars):
        for totalvarsid in range(varcounter, num_vars + initvars):
            # print(f"c {auxvarsid} Tseitin_Variable_{tseitincounter}")
            f.write(f"c {totalvarsid} Tseitin_Variable_{tseitincounter}")
            f.write("\n")
            tseitincounter += 1
    else:
        totalvarsid = varcounter - 1

    ##### Boolean vars are always defined at the end (if they were not predefined in a base model) => Last IDs #####
    for bitvar in bitvarsmap:
        ##### Look for type and width #####
        for auxvardefs in file_vars:
            ##### Matching current with declared variables #####
            if auxvardefs[0] == bitvar:
                auxvardef = auxvardefs
        if auxvardef[2] == 'boolean':
            ##### Count and register new boolean features #####
            if auxvardef[1] == 0:
                totalvarsid += 1
                f.write(f"c {totalvarsid} {bitvar} boolean")
                f.write("\n")
                booleanvarsids.append([bitvar, totalvarsid])
            ##### Register the proper ID of an already defined in the extending model boolean feature #####
            else:
                booleanvarsids.append([bitvar, auxvardef[1]])

    ##### Write the main header in the 'p' section of the DIMACS file #####
    # print(f"p cnf {numvars} {maxrange}")
    f.write(f"p cnf {totalvarsid} {maxrange + initconstraints}")
    f.write("\n")

    ##### Add clauses of the extending model if extending one #####
    if (booleanmodelname):
        with open(booleanmodelname) as input_file:
            input_file_content = input_file.read().splitlines()
            for input_line in input_file_content:
                if input_line[0:4] != "def " and input_line[0:2] != "c " and input_line[0:2] != "p ":
                    f.write(input_line)
                    f.write("\n")
    # print(booleanvarsids)

    # ##### MAIN #####

    # ##### Transform Z3 output to DIMACS CNF NFM #####
    # for c in range(maxrange):
    #     aux = str(subgoal[0][c]).replace("Or(", "")
    #     aux = aux.replace("\n  ", "")
    #     aux = aux.replace("k!", "")
    #     aux = aux.replace("Not(", "-")
    #     aux = aux.replace("))", "")
    #     aux = aux.replace(")", "")
    #     aux = aux.replace(",", "")
    #
    #     ##### Adjust the variables IDs, as Z3 starts in 0, and DIMACS in 1 (larger init_id if extending a model) #####
    #     auxarray = aux.split(' ')
    #     updatedaux = ''
    #     for literalvar in auxarray:
    #         ##### HACK => prevent python considering -0 equivalent to 0 #####
    #         if (literalvar == '-0'):
    #             updatedaux += str(f"-{initvars}") + ' '
    #         else:
    #             ##### Adjust Z3 IDs considering the sign #####
    #             if literalvar.lstrip("-").isnumeric():
    #                 numliteralvar = int(literalvar)
    #                 if numliteralvar < 0:
    #                     updatedaux += str(numliteralvar - initvars) + ' '
    #                 else:
    #                     updatedaux += str(numliteralvar + initvars) + ' '
    #             else:
    #                 ##### All Z3 boolean features are transformed all at once in the next line #####
    #                 updatedaux += str(f"{literalvar}") + ' '
    #
    #     ##### Replace Z3 boolean features by their DIMACS IDs #####
    #     for bv in booleanvarsids:
    #         updatedaux = updatedaux.replace(bv[0], str(bv[1]))
    #     # print(updatedaux+'0')
    #
    #     ##### DIMACS clauses finish with a '0' #####
    #     f.write(updatedaux + '0')
    #
    #     ##### Remove the last 'new line' if it is the last clause #####
    #     if (c < maxrange - 1): f.write("\n")

    # ##### MAIN #####

    f.close()
    end = time.time() - start  # - 0.05
    print(f"Transformation time: {str(end).replace('.', ',')} seconds")
    calculatemedian(filepath)