with open("model.dimacs") as input_file:
    input_file_content = input_file.read().splitlines()
counter = 0
vars = 0
for input_line in input_file_content:
    if input_line[0:2] != 'c ' and input_line[0:2] != 'p ':
        counter += 1
        vars += len(input_line.replace(" 0","").split(' '))
print(str(vars/counter).replace('.', ','))
