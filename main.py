import re
import os

# Define los patrones de tokens
token_patterns = [
    (r'\btext\b', 'PRINT'),
    (r'\bprint\b', 'PRINT'),
    (r'\bresolver\b', 'RESOLVER'),
    (r'"(?:[^"\\]|\\.)*"', 'STRING'),
    (r'\bif\b', 'IF'),
    (r'\bwhile\b', 'WHILE'),
    (r'\bfor\b', 'FOR'),
    (r'\bdef\b', 'DEF'),
    (r'\breturn\b', 'RETURN'),
    (r'\btrue\b', 'TRUE'),
    (r'\bfalse\b', 'FALSE'),
    (r'[0-9]+', 'NUMBER'),
    (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
    (r'[\+\-\*/\^/\=/\~/\?/\¿/]', 'OPERATOR'),
    (r'[\(\)\[\]\{\}\<\>\&.,:;]', 'DELIMITER'),
    (r'\s+', 'WHITESPACE'),
    (r'--.*', 'COMMENT'),
]

def tokenize(code):
    # Crea una lista de tokens a partir del código
    tokens = []
    pos = 0
    line_number = 1
    column_number = 1
    while pos < len(code):
        # Intenta reconocer cada uno de los patrones de tokens
        match = None
        for pattern, token_type in token_patterns:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                value = match.group()
                if token_type != 'WHITESPACE' and token_type != 'COMMENT':
                    tokens.append((token_type, value))
                pos = match.end()
                break
        # Si no se encontró ninguna coincidencia, se produce un error
        if not match:
            raise LexicalError(f"Error de sintaxis en la línea {line_number}, columna {column_number}: Carácter inesperado '{code[pos]}'")
    return tokens
    
def parse(tokens):
    # Función recursiva para procesar las expresiones aritméticas
    def expression():
        if tokens[0][0] == 'PRINT':
            # Elimina el token de impresión de la lista
            tokens.pop(0)
            # Verifica que venga un string a continuación
            string_token = tokens.pop(0)    
            if string_token[0] != 'STRING':
                raise SyntaxError("Se esperaba un string después de 'text' ")
            # Regresa una tupla para indicar una impresión de texto
            return ('STRING', string_token[1])
        def term():
            # Procesa un factor
            def factor():
                token = tokens.pop(0)
                if token[0] == 'RESOLVER':
                    # Si se encuentra un token de tipo 'PRINT', se procesa la expresión que sigue
                    print_expression = expression()
                    return ('RESOLVER', print_expression)
                elif token[0] == 'NUMBER':
                     return ('NUMBER', int(token[1]))
                elif token[0] == 'IDENTIFIER':
                    return ('IDENTIFIER', token[1])
                elif token[0] == 'OPERA':
                    return ('OPERA', token[1])
                elif token[0] == 'STRING':
                     # Regresa una tupla para indicar que se trata de un string
                     return ('STRING', token[1])
                elif token[1] == '(':
                     node = expression()
                     token = tokens.pop(0)
                     if token[1] != ')':
                         if token[1] != ';':
                             raise SyntaxError("Se esperaba ';'")
                         return node
                else:
                     raise SyntaxError("Se esperaba un número, un identificador, un string o '('")
                    # Procesa una lista de factores separados por '*' o '/'
            node = factor()
            while tokens and (tokens[0][0] == 'OPERATOR' and (tokens[0][1] == '*' or tokens[0][1] == '/')) and tokens[0][0] != 'DELIMITER' and tokens[0][0] != 'WHITESPACE':
                token = tokens.pop(0)
                if token[1] == '*':
                    node = ('*', node, factor())
                elif token[1] == '/':
                    node = ('/', node, factor())
            return node
        # Procesa una lista de términos separados por '+' o '-'
        node = term()
        while tokens and (tokens[0][1] == '+' or tokens[0][1] == '-' ):
            token = tokens.pop(0)
            if token[1] == '+':
                node = ('+', node, term())
            elif token[1] == '-':
                node = ('-', node, term())
        return node
    # Comienza el procesamiento por la expresión principal
    node = expression()
    # Verifica que no haya tokens sobrantes
    if tokens:
        raise SyntaxError("Se esperaba el final de la expresión")
    return node

def generate_code(node):
    if node[0] == 'RESOLVER':
        # Genera el código objeto para la expresión hija del nodo
        expression_code = generate_code(node[1])
        # Agrega una instrucción para imprimir el resultado de evaluar la expresión
        return f"print({expression_code})"
    elif node[0] == 'PRINT':
        # Genera el código objeto para la expresión hija del nodo
        expression_code = generate_code(node[1])
        # Agrega una instrucción para imprimir el resultado de evaluar la expresión
        return f"print({expression_code})"
    elif node[0] == 'NUMBER':
        return str(node[1])
    elif node[0] == 'IDENTIFIER':
        return node[1]
    elif node[0] == 'STRING':
        return f'{node[1]}'
    elif node[0] in ('+', '-', '*', '/'):
        return f"({generate_code(node[1])} {node[0]} {generate_code(node[2])})"
    else:
        raise ValueError(f"Nodo desconocido: {node[0]}")
    
def compile(code):
    # Genera la lista de tokens a partir del código fuente
    tokens = tokenize(code)
    # Verifica la gramática del código y construye el AST
    ast = parse(tokens)
    # Recorre el AST y genera el código objeto
    obj_code = generate_code(ast)
    return obj_code

# Clase para los errores léxicos
class LexicalError(Exception):
    def __init__(self, message):
        super().__init__(message)

# Prueba el analizador léxico con algunos códigos
try:
    filename2 = "archivo.ty"
    file_name = "main.ty"
    _, ext1 = os.path.splitext(file_name)
    _, ext2 = os.path.splitext(filename2)
    if ext1 == ext2:
        f = open(file_name, 'r')
        lineas = f.readlines()
        f.close()
        # lee cada linea del archivo para compilarlas
        for linea in lineas:
              print(eval(compile(linea)))
    else:
         print("Se desconose la extension: *%s" %ext1)
except LexicalError as e:
    print(e)
    
