import re
import copy

def tokenizer(input):
    current = 0
    tokens = []

    while (current < input.length()):
        char = input[current]

        if (char == '('):
            tokens.append({
                'type' : 'paren',
                "value" : '('

            })
            current++
            continue
            
        if (char == ')':
            tokens.append({
                'type':'paren',
                'value':')'
            })
            current++
            continue
