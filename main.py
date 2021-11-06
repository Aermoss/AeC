import sys
import os

def open_file(file_name):
    return open(file_name, "r").read()

def lexer(code):
    tokens = []
    token = ""
    string = ""
    string_state = False

    for char in code:
        token = token + char

        if token == " " or token == "\n":
            if not string_state:
                token = ""

        elif token == "\"":
            if string_state:
                tokens.append(string)
                string = ""
                string_state = False

            else:
                string_state = True

            token = ""

        elif string_state:
            string = string + token
            token = ""

        elif token == "print":
            tokens.append("PRINT")
            token = ""

    return tokens

def parser(tokens):
    functions = []
    variables = []
    pos = 0

    while True:
        if len(tokens) - 1 < pos:
            break

        elif tokens[pos] == "PRINT":
            functions.append("PRINT")
            variables.append(tokens[pos + 1])
            pos = pos + 2

    return functions, variables

def generate_asm(functions, variables, file_name):
    function_code = ""
    variable_code = ""

    function_amount = 0
    variable_amount = 0

    code = ""

    code = code + "global _start\n"
    code = code + "\nsection .text\n"
    code = code + "\n_start:\n"

    for i in functions:
        if i == "PRINT":
            function_amount = function_amount + 1
            function_code = function_code + f"    mov rax, 0x1\n"
            function_code = function_code + f"    mov rdi, 0x1\n"
            function_code = function_code + f"    mov rsi, msg{function_amount}\n"
            function_code = function_code + f"    mov rdx, msglength{function_amount}\n"
            function_code = function_code + f"    syscall\n\n"

    function_code = function_code + "    mov rax, 0x3C\n"
    function_code = function_code + "    mov rdi, 0x0\n"
    function_code = function_code + "    syscall\n"

    code = code + function_code

    for i in variables:
        variable_amount = variable_amount + 1
        variable_code = variable_code + f"    msg{variable_amount}: db \"{i}\", 0xA\n"
        variable_code = variable_code + f"    msglength{variable_amount}: EQU $ - msg{variable_amount}\n"

    code = code + "\nsection .data\n"
    code = code + variable_code
    
    head, tail = os.path.split(file_name)
    file_name, ext = os.path.splitext(tail)

    file = open(f"{file_name}.asm", "w")
    file.write(code)
    file.close()

    os.system(f"nasm -f elf64 -o {file_name}.o {file_name}.asm")
    os.system(f"ld -o {file_name} {file_name}.o")
    os.system(f"./{file_name}")

def main():
    file_name = sys.argv[1]
    functions, variables = parser(lexer(open_file(file_name)))
    generate_asm(functions, variables, file_name)

if __name__ == "__main__":
    main()