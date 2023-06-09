from TinyCompiler import tokenizer, parser, transformer, code_generator, compiler
import json

input = '(add 2 (subtract 4 2))'
output = 'add(2, subtract(4, 2));'

tokens = [
    {'type': 'paren',  'value': '('},
    {'type': 'name',   'value': 'add'},
    {'type': 'number', 'value': '2'},
    {'type': 'paren',  'value': '('},
    {'type': 'name',   'value': 'subtract'},
    {'type': 'number', 'value': '4'},
    {'type': 'number', 'value': '2'},
    {'type': 'paren',  'value': ')'},
    {'type': 'paren',  'value': ')'}
]

ast = {
    'type': 'Program',
    'body': [{
        'type': 'CallExpression',
        'name': 'add',
        'params': [{
            'type': 'NumberLiteral',
            'value': '2'
        }, {
            'type': 'CallExpression',
            'name': 'subtract',
            'params': [{
                'type': 'NumberLiteral',
                'value': '4'
            }, {
                'type': 'NumberLiteral',
                'value': '2'
            }]
        }]
    }]
}

new_ast = {
    'type': 'Program',
    'body': [{
        'type': 'ExpressionStatement',
        'expression': {
            'type': 'CallExpression',
            'callee': {
                'type': 'Identifier',
                'name': 'add'
            },
            'arguments': [{
                'type': 'NumberLiteral',
                'value': '2'
            }, {
                'type': 'CallExpression',
                'callee': {
                    'type': 'Identifier',
                    'name': 'subtract'
                },
                'arguments': [{
                    'type': 'NumberLiteral',
                    'value': '4'
                }, {
                    'type': 'NumberLiteral',
                    'value': '2'
                }]
            }]
        }
    }]
}

assert json.dumps(tokenizer(input)) == json.dumps(tokens), 'Tokenizer should turn `input` string into `tokens` array'
assert json.dumps(parser(tokens)) == json.dumps(ast), 'Parser should turn `tokens` array into `ast`'
assert json.dumps(transformer(ast)) == json.dumps(new_ast), 'Transformer should turn `ast` into a `newAst`'
assert code_generator(new_ast) == output, 'Code Generator should turn `newAst` into `output` string'
assert compiler(input) == output, 'Compiler should turn `input` into `output`'

print('All Passed!')
