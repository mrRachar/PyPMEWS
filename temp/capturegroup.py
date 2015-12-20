number = 0

def getcaturegroup(string: str):
    global number
    string = string.lstrip(' \t')
    if not ':' in string:
        return False
    name = string[:string.index(':')]
    isarray = name.endswith('[]')
    if isarray:
        name = name[:-2]
    if name == '':
        number += 1
        return str(number -1) if not isarray else str(number -1) + '()'
    if not name[0].isalpha() or not all(letter.isalnum() for letter in name[1:]):
        return False
    else:
        return name + ('' if not isarray else '()')
    
