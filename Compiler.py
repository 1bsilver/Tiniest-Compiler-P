import re
import copy

def tokenizer(input):
    current = 0
    tokens = []

    num_REGEX = re.compile(r"[0-9]");
    alpha_REGEX = re.compile(r"[a-z]", re.I);
    whitespace = re.compile(r"\s");
    quote = re.compile(r"\"\[.+\]\"")

    while (current < input.length()):
        char = input[current]

        if (char == '('):
            tokens.append({
                'type' : 'lparen',
                "value" : '('

            })
            current = current + 1
            continue
            
        if (char == ')'):
            tokens.append({
                'type':'rparen',
                'value':')'
            })
            current = current + 1
            continue

        if re.match(whitespace, char):
            current = current+1
            continue

        if re.match(num_REGEX, char):
            value = ''
            while re.match(num_REGEX, char):
                value += char
                current = current + 1
                char = input[current]

            tokens.append({
                'type':'number',
                'value':(value)
            })
            
            continue

        if re.match(quote, char):
            value = ''
            while not re.match(quote, char):
                value += char
                current = current + 1
                char = input[current]

            tokens.append({
                'type': 'string',
                'value':value
            })
            continue


        if re.match(alpha_REGEX, char):
            value = ''
            while re.match(alpha_REGEX, char):
                value += char
                current = current + 1
                char = input[current]

            tokens.append({
                'type': 'name',
                'value':value
            })

            continue

        raise ValueError('I dont know what this character is: ' + char);

    return tokens

def parser(tokens):

    global current
    current = 0

    def walk():
        token = tokens[current]

        if (token.get('type') == 'number'):
            current = current + 1
            return {
                'type': 'NumberLiteral',
                'value':token.get('value')
            }

        if token.get('type') == 'string':
            current = current + 1
            return {
                'type' : 'StringLiteral',
                'value' : token.get('value')
            }

        if (token.get('type')=='lparen'):
            current = current + 1
            node = {
                'type':'CallExpression',
                'name': token.get('value'),
                'params':[]
            }

            current = current + 1

            while token.get('type') != 'rparent':
                node['params'].append(walk())
                token = tokens[current]

            current = current + 1
            return node

        raise TypeError(token.get('type'))

    ast = {
        'type': 'Program',
        'body': []
    }
    
    while current < len(tokens):
        ast['body'].append(walk())
    return ast

    def traverser(ast, visitor):
        def traverseArray(array, parent):
            for child in arrays:
                traverseNode(child,parent)

        def traverseNode(node,parent):
            method = visitor.get(node['type'])
            
            if method:
                methof(node,parent)

            if node['type'] == 'Program':

                traverseArray(node['body'], node)

            elif node['type'] == 'CallExpression':

                traverseArray(node['body'], node)

            elif (node['type'] == ('NumberLiteral') or node['type'] == 'StringLiteral'):
                0
            
            else:
                raise TypeError(node['type'])

        traverseNode(ast, None)

    def transformer(ast):
        
        newAst = {
            'type': 'Program',
            'body': []
        }

        oldAst = ast

        ast = copy.deepcopy(oldAst)
        ast['_context'] = newAst.get('body')

        def NumberLiteralVisitor(node, parent):
            parent['_context'].append({
                'type':'NumberLiteral',
                'value':node['value']
            })

        def CallExpressionVisitor(node, parent):
            expression = {
                'type':'CallExpression',
                'callee': {
                    'type':'Identifier',
                    'name':node['name']
                },
                'arguments': []

            }

            node['_context'] = expression['arguments']

            if parent['type'] != 'CallExpression':
                expression = {
                    'type':'ExpressionStatement',
                    'expression': expression
                }
            parent['_context'].append(expression)

        traverser(ast, {
            'NumberLiteral' : NumberLiteralVisitor,
            'CallExpression': CallExpressionVisitor
        })

        return newAst
        
        