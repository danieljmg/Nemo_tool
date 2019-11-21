def readNFM(filepath, vars, cts):
    with open(filepath) as input_file:
        input_file_content = input_file.read().splitlines()
    for input_line in input_file_content:
        #print(input_line)
        if 'def' == input_line[:3]:
            # It is a variable definition

            if ' bool ' in input_line:
                boolvardef = input_line.split(' ')
                vars.append([boolvardef[1], int(boolvardef[3]), 'boolean'])
            elif ':' in input_line:
                var_sign = ''
                w = 0
                var_ranges = input_line.split('def ')[1].split(' [')
                # It is a range definition
                # Retrieve the range of this number defition to calculate the sign and widths
                range = var_ranges[1][:-1].split(':')

                # Empty limit is by default 0
                if range[0] == '': range[0] = '0'
                if range[1] == '': range[1] = '0'

                # Converts String List to a Int List
                range = list(map(int, range))
                if range[0] < 0:
                    # Negative numbers in play
                    var_sign = 'signed'
                    if abs(range[1]) >= abs(range[0]) - 1:
                        # Two's complement where the top limit is the bigger number
                        w = range[1].bit_length() + 1
                    else:
                        # Two's complement where the bottom limit is the bigger number e.g.: [-7:3]
                        w = (range[0] + 1).bit_length() + 1
                    # Add constraint if the bottom range is not Pw(2)
                    if (abs(range[0]) / (2 ** (w - 1)) != 1.0):
                        cts.append(f'{var_ranges[0]} > {range[0] - 1}')
                    else:
                        cts.append(f'{var_ranges[0]} >= {range[0]}')
                    # Add constraint if the top range is not Pw(2)
                    if w != 1 and ((abs(range[1]) + 1) / (2 ** (w - 1)) != 1.0):
                        cts.append(f'{var_ranges[0]} < {range[1] + 1}')
                    else:
                        cts.append(f'{var_ranges[0]} <= {range[1]}')
                else:
                    var_sign = 'unsigned'
                    w = range[1].bit_length()
                    if range[0] != '' and range[0] > 0:
                        cts.append(f'{var_ranges[0]} > {range[0] - 1}')
                    else:
                        cts.append(f'{var_ranges[0]} >= 0')
                    if w != 1 and ((abs(range[1]) + 1) / (2 ** w) != 1.0):
                        cts.append(f'{var_ranges[0]} < {range[1] + 1}')
                    else:
                        cts.append(f'{var_ranges[0]} <= {range[1]}')

                # vars.append(input_line.split('def ')[1].split(' [')[0])
                vars.append([var_ranges[0], w, var_sign])

            elif ',' in input_line:
                var_sign = ''
                w = 0
                var_ranges = input_line.split('def ')[1].split(' [')
                # It is enumerated
                var_values = var_ranges[1][:-1].split(',')

                # Converts String List to a Int List
                var_values = list(map(int, var_values))

                # Add constraints
                aux_constraint = 'Or('
                for var_value in var_values:
                    aux_constraint += f'{var_ranges[0]} == {var_value}, '
                cts.append(aux_constraint[:-2]+')')

                # Lower Limit
                range[0] = var_values[0]

                # Upper Limit
                range[1] = var_values[-1]

                if range[0] < 0:
                    # Negative numbers in play
                    var_sign = 'signed'
                    if abs(range[1]) >= abs(range[0]) - 1:
                        # Two's complement where the top limit is the bigger number
                        w = range[1].bit_length() + 1
                    else:
                        # Two's complement where the bottom limit is the bigger number e.g.: [-7:3]
                        w = (range[0] + 1).bit_length() + 1
                else:
                    var_sign = 'unsigned'
                    w = range[1].bit_length()
                # vars.append(input_line.split('def ')[1].split(' [')[0])
                vars.append([var_ranges[0], w, var_sign])


            else:
                var_sign = ''
                w = 0
                var_ranges = input_line.split('def ')[1].split(' [')
                # It is a constant
                var_value = int(var_ranges[1][:-1])
                if var_value >= 0:
                    var_sign = 'unsigned'
                    w = var_value.bit_length()
                else:
                    var_sign = 'signed'
                    w = var_value.bit_length() + 1
                vars.append([var_ranges[0], w, var_sign])
                cts.append(f'{var_ranges[0]} == {var_value}')

        elif 'ct' == input_line[:2]:
            # It is a constraint definition
            cts.append(input_line.split('ct ')[1])

    ##### Adjust variables widths #####
    for i, var_check_a in enumerate(vars):
        if(var_check_a[2] != 'boolean'):
            for ct in cts:
                for j, var_check_b in enumerate(vars):
                    if (var_check_b[2] != 'boolean'):
                        if (var_check_a[0] in ct) and (var_check_b[0] in ct):
                            # Adjusting signs first
                            if (var_check_a[2] == 'signed') and (var_check_b[2] == 'unsigned'):
                                vars[j][2] = 'signed'
                            elif (var_check_b[2] == 'signed') and (var_check_a[2] == 'unsigned'):
                                vars[i][2] = 'signed'
                            # Adjusting widths
                            if int(var_check_a[1]) > int(var_check_b[1]):
                                vars[j][1] = vars[i][1]
                            elif int(var_check_b[1]) > int(var_check_a[1]):
                                vars[i][1] = vars[j][1]

    ##### Optimise for unsigned OPs #####
    for i, ct in enumerate(cts):
        unsigned_op = -1
        for var_check in vars:
            if (var_check[0] in ct) and (var_check[2] == 'unsigned'): unsigned_op = 1
        if unsigned_op == 1:
            if ' < ' in ct:
                ct = ct.split(' < ')
                cts[i] = f"ULT({ct[0]}, {ct[1]})"
            elif ' > ' in ct:
                ct = ct.split(' > ')
                cts[i] = f"UGT({ct[0]}, {ct[1]})"
            elif ' >= ' in ct:
                ct = ct.split(' >= ')
                cts[i] = f"ULE({ct[0]}, {ct[1]})"
            elif ' <= ' in ct:
                ct = ct.split(' <= ')
                cts[i] = f"UGE({ct[0]}, {ct[1]})"
            # UDiv and URem TODO

    ##### Translate Boolean ops to Z3 format #####
    for i, ct in enumerate(cts):
        if ' -> ' in ct:
            ct = ct.split(' -> ')
            cts[i] = f"Implies({ct[0]}, {ct[1]})"

    ##### Optimise for implicit bit-width constraints #####
    for var_optimise in vars:
        toerase = []
        if var_optimise[2] == 'unsigned':
            toerases = [f'{var_optimise[0]} >= 0', f'{var_optimise[0]} > 1',
                        f'{var_optimise[0]} <= {(2 ** var_optimise[0]) - 1}',
                        f'{var_optimise[0]} < {(2 ** var_optimise[0])}']
            for toerase in toerases:
                for i, ct_eval in enumerate(cts):
                    if toerase == ct_eval:
                        del cts[-i]
                        break
        elif var_optimise[2] == 'signed':
            toerases = [f'{var_optimise[0]} >= -{(2 ** (var_optimise[1] - 1)) - 1}', f'{var_optimise[1]} > -{(2 ** (var_optimise[1] - 1))}',
                        f'{var_optimise[0]} <= {(2 ** (var_optimise[1] - 1)) - 1}',
                        f'{var_optimise[0]} < {(2 ** (var_optimise[1] - 1))}']
            for toerase in toerases:
                for i, ct_eval in enumerate(cts):
                    if toerase == ct_eval:
                        del cts[-i]
                        break

    return (vars, cts)