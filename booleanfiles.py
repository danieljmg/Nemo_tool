filepath = "modeltest.dimacs"
with open(filepath) as input_file:
    input_file_content = input_file.read().splitlines()

varcount = 0
for input_line in input_file_content:
    if('p cnf ' == input_line[0:6]):
        varcount += 1
        print(int(input_line[6:].split(' ')[0]))