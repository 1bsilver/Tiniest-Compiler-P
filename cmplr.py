import re
import copy

def tokenizer(input_program):

    # A `current` variable for tracking our position in the code like a cursor.
    current = 0
    # And a `tokens` array for pushing our tokens to.
    tokens = []
    #* this is a little optimization, since `input_program` length won't change
    # in the excecution it is safe to get the length at the beginning.
    program_length = len(input_program)
    
    #* this is to simplify the regexp's, since in JS regexp can be
    # inline and look very pretty.

    REGEX_WHITESPACE = re.compile(r"\s");
    REGEX_NUMBERS = re.compile(r"[0-9]");
    REGEX_LETTERS = re.compile(r"[a-z]", re.I);

    # We start by creating a `while` loop where we are setting up our `current`
    # variable to be incremented as much as we want `inside` the loop.
    #
    # We do this because we may want to increment `current` many times within a
    # single loop because our tokens can be any length.
    while current < program_length:

        # We're also going to store the `current` character in the `input`.
        char = input_program[current]

        # The first thing we want to check for is an open parenthesis. This will
        # later be used for `CallExpressions` but for now we only care about the
        # character.
        #
        # We check to see if we have an open parenthesis:
        if char == '(':
            tokens.append({
                'type': 'lparen',
                'value': '('
            })

            # Then we increment `current`
            current = current+1
            # And we `continue` onto the next cycle of the loop.
            continue
        
        # Next we're going to check for a closing parenthesis. We do the same exact
        # thing as before: Check for a closing parenthesis, add a new token,
        # increment `current`, and `continue`.
        if char == ')':
            tokens.append({
                'type': 'rparen',
                'value': ')'
            })
            current = current+1
            continue
        # Moving on, we're now going to check for whitespace. This is interesting
        # because we care that whitespace exists to separate characters, but it
        # isn't actually important for us to store as a token. We would only throw
        # it out later.
        #
        # So here we're just going to test for existence and if it does exist we're
        # going to just `continue` on.
        if re.match(REGEX_WHITESPACE, char):
            current = current+1
            continue

        # The next type of token is a number. This is different than what we have
        # seen before because a number could be any number of characters and we
        # want to capture the entire sequence of characters as one token.
        #
        #   (add 123 456)
        #        ^^^ ^^^
        #        Only two separate tokens
        #
        # So we start this off when we encounter the first number in a sequence.

        if re.match(REGEX_NUMBERS, char):
            # We're going to create a `value` string that we are going to push
            # characters to.
            value = ''
            
            # Then we're going to loop through each character in the sequence until
            # we encounter a character that is not a number, pushing each character
            # that is a number to our `value` and incrementing `current` as we go.
            while re.match(REGEX_NUMBERS, char):
                value += char
                current = current+1
                char = input_program[current];
            # After that we push our `number` token to the `tokens` array.
            tokens.append({
                'type': 'number',
                'value': value
            })
            # And we continue on.
            continue

        # The last type of token will be a `name` token. This is a sequence of
        # letters instead of numbers, that are the names of functions in our lisp
        # syntax.
        #
        #   (add 2 4)
        #    ^^^
        #    Name token
        #

        if re.match(REGEX_LETTERS, char):
            value = ''
            # Again we're just going to loop through all the letters pushing them to
            # a value.
            while re.match(REGEX_LETTERS, char):
                value += char
                current = current+1
                char = input_program[current]

            # And pushing that value as a token with the type `name` and continuing.
            tokens.append({
                'type': 'name',
                'value': value
            })

            continue
        # Finally if we have not matched a character by now, we're going to throw
        # an error and completely exit.
        raise ValueError('I dont know what this character is: ' + char);
    #Then at the end of our `tokenizer` we simply return the tokens array.
    return tokens
        
def parser(tokens):
    global current
    current = 0
    def walk():
        global current
        token = tokens[current]
        if token.get('type') == 'number':
            current = current + 1
            return {
                'type': 'NumberLiteral',
                'value': token.get('value')
            }
        if token.get('type') == 'lparen':
            current = current + 1
            token = tokens[current]
            node = {
                'type': 'CallExpression',
                'name': token.get('value'),
                'params': []
            }

            current = current + 1
            token = tokens[current]
            while token.get('type') != 'rparen':
                node['params'].append(walk());
                token = tokens[current]
            current = current + 1
            return node
        raise TypeError(token.get('type'))
    ast = {
        'type': 'Program',
        'body': []
    }
    token_length = len(tokens)
    while current < token_length:
        ast['body'].append(walk())
    return ast

def traverser(ast, visitor):
    def traverseArray(array, parent):
        for child in array:
            traverseNode(child, parent)
    
    def traverseNode(node, parent):
        method = visitor.get(node['type'])
        if method:
            method(node, parent)
        if node['type'] == 'Program':
            traverseArray(node['body'], node)
        elif node['type'] == 'CallExpression':
            traverseArray(node['params'], node)
        elif node['type'] == 'NumberLiteral':
            # do nothing
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
            'type': 'NumberLiteral',
            'value': node['value']
        })
    def CallExpressionVisitor(node, parent):
        expression = {
            'type': 'CallExpression',
            'callee': {
                'type': 'Identifier',
                'name': node['name']
            },
            'arguments': []
        }
        
        node['_context'] = expression['arguments']

        if parent['type'] != 'CallExpression':
            expression = {
                'type': 'ExpressionStatement',
                'expression': expression
            }
        parent['_context'].append(expression)

    traverser( ast , {
        'NumberLiteral': NumberLiteralVisitor,
        'CallExpression': CallExpressionVisitor 
    })
    
    return newAst

def codeGenerator(node):
    if node['type'] == 'Program':
        return '\n'.join([code for code in map(codeGenerator, node['body'])])
    elif node['type'] == 'ExpressionStatement':
        expression = codeGenerator(node['expression']) 
        return '%s;' % expression
    elif node['type'] == 'CallExpression':
        callee = codeGenerator(node['callee']) 
        params = ', '.join([code for code in map(codeGenerator, node['arguments'])])
        return "%s(%s)" % (callee, params)
    elif node['type'] == 'Identifier':
        return node['name']
    elif node['type'] == 'NumberLiteral':
        return node['value']
    else:
        raise TypeError(node['type'])

def compiler(input_program):

    tokens = tokenizer(input_program)
    ast    = parser(tokens)
    newAst = transformer(ast)
    output = codeGenerator(newAst)
    return output

def main():
    #test 
    input = "(add 2 (subtract 4 2))"
    output = compiler(input)
    print(output)


if __name__ == "__main__":
    main()