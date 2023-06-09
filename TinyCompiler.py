import re


def tokenizer(input):
    """
    Function to convert a string of code into an array of tokens.
    A token is an object that describes a piece of code.
    :param input: string of code
    :return: array of tokens
    """

    current = 0
    tokens = []

    while current < len(input):

        char = input[current]

        if char == '(':
            tokens.append({
                'type': 'paren',
                'value': '(',
            })
            current += 1
            continue

        if char == ')':
            tokens.append({
                'type': 'paren',
                'value': ')',
            })
            current += 1
            continue

        WHITESPACE = re.compile('\s')
        if WHITESPACE.match(char):
            current += 1
            continue

        NUMBERS = re.compile('[0-9]')
        if NUMBERS.match(char):
            value = ''
            while NUMBERS.match(char):
                value += char
                current += 1
                if current < len(input):
                    char = input[current]
                else:
                    break
            tokens.append({'type': 'number', 'value': value})
            continue

        if char == '"':
            value = ''
            char = input[current + 1]
            while char != '"':
                value += char
                current += 1
                char = input[current + 1]
            current += 2
            tokens.append({'type': 'string', 'value': value})
            continue

        LETTERS = re.compile('[a-z]', re.I)
        if LETTERS.match(char):
            value = ''
            while LETTERS.match(char):
                value += char
                current += 1
                if current < len(input):
                    char = input[current]
                else:
                    break
            tokens.append({'type': 'name', 'value': value})
            continue

        raise TypeError('I dont know what this character is: ' + char)

    return tokens


def parser(tokens):
    """
    Function to convert an array of tokens into an abstract syntax tree (AST).
    An AST is a representation of the code that retains its structure.
    :param tokens: array of tokens
    :return: AST
    """

    current = 0

    def walk():
        nonlocal current

        token = tokens[current]

        if token['type'] == 'number':
            current += 1
            return {
                'type': 'NumberLiteral',
                'value': token['value'],
            }

        if token['type'] == 'string':
            current += 1
            return {
                'type': 'StringLiteral',
                'value': token['value'],
            }

        if token['type'] == 'paren' and token['value'] == '(':
            current += 1
            token = tokens[current]

            node = {
                'type': 'CallExpression',
                'name': token['value'],
                'params': [],
            }

            current += 1
            token = tokens[current]

            while (
                token['type'] != 'paren' or 
                (token['type'] == 'paren' and token['value'] != ')')
            ):
                node['params'].append(walk())
                token = tokens[current]

            current += 1
            return node

        raise TypeError(token['type'])

    ast = {
        'type': 'Program',
        'body': [],
    }

    while current < len(tokens):
        ast['body'].append(walk())

    return ast


def traverser(ast, visitor):
    """
    Function to traverse an AST and call methods on visitor for each node.
    :param ast: AST
    :param visitor: object with methods to call
    :return: None
    """

    def traverse_array(array, parent):
        for child in array:
            traverse_node(child, parent)

    def traverse_node(node, parent):
        methods = visitor.get(node['type'])

        if methods and 'enter' in methods:
            methods['enter'](node, parent)

        if node['type'] == 'Program':
            traverse_array(node['body'], node)
        elif node['type'] == 'CallExpression':
            traverse_array(node['params'], node)
        elif node['type'] in ('NumberLiteral', 'StringLiteral'):
            pass
        else:
            raise TypeError(node['type'])

        if methods and 'exit' in methods:
            methods['exit'](node, parent)

    traverse_node(ast, None)


def transformer(ast):
    """
    Function to transform an AST into a new AST.
    :param ast: AST
    :return: new AST
    """

    new_ast = {
        'type': 'Program',
        'body': [],
    }

    ast['_context'] = new_ast['body']

    def number_literal(node, parent):
        parent['_context'].append({
            'type': 'NumberLiteral',
            'value': node['value'],
        })

    def string_literal(node, parent):
        parent['_context'].append({
            'type': 'StringLiteral',
            'value': node['value'],
        })

    def call_expression(node, parent):
        expression = {
            'type': 'CallExpression',
            'callee': {
                'type': 'Identifier',
                'name': node['name'],
            },
            'arguments': [],
        }

        node['_context'] = expression['arguments']

        if parent['type'] != 'CallExpression':
            expression = {
                'type': 'ExpressionStatement',
                'expression': expression,
            }

        parent['_context'].append(expression)

    visitor = {
        'NumberLiteral': {'enter': number_literal},
        'StringLiteral': {'enter': string_literal},
        'CallExpression': {'enter': call_expression},
    }

    traverser(ast, visitor)

    return new_ast





def code_generator(node):
    """
    Function to generate code from an AST.
    :param node: AST node
    :return: code
    """

    if node['type'] == 'Program':
        return '\n'.join(map(code_generator, node['body']))
    elif node['type'] == 'ExpressionStatement':
        return code_generator(node['expression']) + ';'
    elif node['type'] == 'CallExpression':
        return code_generator(node['callee']) + '(' + ', '.join(map(code_generator, node['arguments'])) + ')'
    elif node['type'] == 'Identifier':
        return node['name']
    elif node['type'] == 'NumberLiteral':
        return str(node['value'])
    elif node['type'] == 'StringLiteral':
        return '"' + node['value'] + '"'
    else:
        raise TypeError('Unknown node type: ' + node['type'])

def compiler(input):
    tokens = tokenizer(input)
    ast = parser(tokens)
    new_ast = transformer(ast)
    output = code_generator(new_ast)
    return output
