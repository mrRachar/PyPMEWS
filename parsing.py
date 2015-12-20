from datatypes import *
from typeenforcing import typed

## FIXME # get rid of the random node at the front of trees with set branches
## TODO # CLEAN!

def rcprint(value, indent=0):
    if indent > 20:
        return
    if isinstance(value, Tree):
        print(' ' *indent*4, '{}({})'.format(value.__class__, value.name))
        rcprint(value.tree, indent+4)
    else:
        print(' ' *indent*4, '{}({})'.format(value.__class__, value.value))
    for x in value.branches:
        rcprint(x, indent+1)


class ParserMeta(type):
    def __call__(self, expr: str):
        self.capturenumber = 0 # Reset capture number
        return Tree(self.parse(expr))

class Parser(metaclass=ParserMeta):
    capturenumber = 0 # Number for enumerated capture groups

    @classmethod
    def parse(cls, expr: str) -> Node:
        index = 0
        base = node = Join()
        while index < len(expr):
            letter = expr[index]
            if letter == '\\':
                index += 1
                char = {
                    'n': '\n',
                    'd': '0-9',
                    'c': 'alpha',
                    's': 'space',
                    'w': 'alphanum'
                }.get(expr[index].lower(), expr[index])
                node <<= Node(char, (char != expr[index] and expr[index].isupper()))

            elif letter in '(':
                startoffset, closeoffset = index + 1, cls.findbalanced("(", ")", expr[index + 1:])
                group = Tree()
                node <<= group
                node = group.tree

                if cls.getcaturegroup(expr[startoffset:index + closeoffset.start]):
                    length, group.name = cls.getcaturegroup(expr[startoffset:index + closeoffset.start], sideeffect=True)
                    startoffset += length + 1

                # See if there is a | in the shallowest depth, if so switch to 'or'
                if cls.shallowfind(r'\|', r'\(', r'\)', expr[startoffset:index + closeoffset.start]):
                    if expr[startoffset] == '^':
                        closeoffset += 1
                        group.negate = True
                    for expression in cls.shallowsplit(r'\|', r'\(', r'\)', expr[startoffset:index + closeoffset.start]):
                        node.add(cls.parse(expression))
                else:
                    node <<= cls.parse(expr[startoffset:index + closeoffset.start])
                node = group #get back on track, leaving group
                index += closeoffset.end - 1  # -1 to account for later +1

            elif letter == '[':
                group = Tree()
                node <<= group
                node = group.tree
                if expr[index + 1] == '^':
                    index += 1
                    group.negate = True
                closer = cls.unescapedindex(']', expr[index:]) #Change following to match 'Span Pattern' #CHECK DE-RE WORKED
                end, over = index + closer.start, closer.end
                for letter in cls.getletters(expr[index + 1:end]):
                    node.add(Node(letter))
                node = group
                index += over - 1

            elif letter == '{':
                if expr[index + 1] == '%':
                    index += 1
                    node.reverse = True
                contents = expr[index + 1:expr.index('}', index)]
                joiner = Join()
                firstvalid = True
                for valid, x in cls.repeatrange(contents):
                    if x == 0 and valid:
                        node.parent.add(joiner) # fixme greedless parent? aswell?
                        continue
                    if 1 < x:
                        node >>= node.copy()
                    if valid and firstvalid:
                        firstvalid = False
                        node.add(joiner)
                index += 2 + len(contents)
                node = joiner
                continue

            elif letter == '*':
                greedless = expr[index + 1] == '%' if len(expr) > index + 1 else False
                node.reverse = greedless
                joiner = Join()
                node.parent.branches.insert(len(node.parent.branches) if not greedless else 0, joiner)
                node <<= node
                node.add(joiner)
                index += 1 + greedless
                node = joiner
                continue

            elif letter == '+':
                greedless = expr[index + 1] == '%' if len(expr) > index + 1 else False
                node.reverse = greedless
                node <<= node
                index += 1 + greedless
                continue

            elif letter == '?':
                greedless = expr[index + 1] == '%' if len(expr) > index + 1 else False
                joiner = Join()
                node.parent.branches.insert(len(node.parent.branches) if not greedless else 0, joiner)
                node.add(joiner)
                index += 1 + greedless
                node = joiner
                continue

            elif letter == '.':
                node <<= Node('any')
            else:
                node <<= Node(letter)

            index += 1
        return base

    @staticmethod
    @typed
    def findbalanced(opener: str, closer: str, string: str) -> Span:
        depth = 1
        for i, char in enumerate(string + ' '):  # Work out why space needed
            if depth == 0:
                break
            elif string[i:].startswith(opener):
                depth += 1
            elif string[i:].startswith(closer):
                depth -= 1
        else:
            raise ValueError("Unbalanced brackets")
        return Span(i, i + len(closer))

    @classmethod
    @typed
    def findbalancedpair(cls, opener: str, closer: str, string: str) -> tuple:
        opening = Span(string.index(opener), length=len(opener))
        closing = cls.findbalanced(opener, closer, string[opening.end + 1:])
        return opening, closing + opening.end

    @staticmethod
    @typed
    def getletters(string: str) -> list:
        letters = []
        index = 0
        while index < len(string):
            stringcont = string[index:]
            if string[index] == '#' and '#' in string[index+1:]:
                index += 1 #pass by first '#'
                letters.append(string[index:string.index('#', index)]) #HERE
                index += string.index('#', index)
            elif len(stringcont) > 1 and stringcont[1] == '-':
                letters.append(string[index:index + 3])
                index += 3
            elif len(stringcont) > 1 and stringcont[0] == '\\':
                char = {
                    'n': '\n',
                    'd': '0-9',
                    'c': 'alpha',
                    's': 'space',
                    'w': 'alphanum'
                }.get(stringcont[1], stringcont[1])
                letters.append(char)
                index += 2
            else:
                letters.append(stringcont[0])
                index += 1
        return letters

    @staticmethod
    @typed
    def repeatrange(string: str):
        string = string.strip()

        @typed
        def getrange(string: str):
            if '-' not in string:
                return None
            strings = (number.strip('\t ') for number in string.split('-'))
            if not all(number.isdigit() or not number for number in strings):
                return None
            return strings


        if string.isdigit():
            stop = int(string)
            yield from ((False, x) for x in range(1, stop))
            yield True, stop
        elif getrange(string):
            start, stop = (int(x) if x else backup
                           for x, backup
                           in zip(getrange(string), (0, 1094)))
            yield from ((False, x) for x in range(1, start) if int(x) > 0)
            yield from ((True, x) for x in range(start, stop+1) if int(x) >= 0)
        else:
            raise ValueError('Bad repetition value, {}'.format(string))

    @classmethod
    @typed
    def shallowfind(cls, needle: str, opener: str, closer: str, string: str) -> (Span, bool):
        if cls.countunescaped(opener, string) != cls.countunescaped(closer, string):  # When there aren't as many closing brackets as opening brackets
            raise ValueError('Unbalanced brackets, {!r}'.format(string))  # the string must be invalid, one must be started without being closed

        offset = 0
        while cls.unescapedindex(opener, string):
            openermatch, closermatch = cls.findbalancedpair(opener, closer, string)
            if needle in string[:openermatch.start]:
                return Span(offset + string[:openermatch.start].index(needle), length=len(needle))
            string = string[closermatch.end:]
            offset += closermatch.end

        if needle in string:
            return Span(offset + string.index(needle), length=len(needle))
        return False

    @staticmethod
    @typed
    def countunescaped(needle: str, haystack: str, start: int=0) -> int:
        count = 0
        for i, letter in enumerate(haystack[start:]):
            if letter == needle and haystack[i-1] != '\\':
                count += 1
        return count

    @staticmethod
    @typed
    def unescapedindex(needle: str, haystack: str, start: int=0) -> (Span, bool):
        for i, letter in enumerate(haystack[start:]):
            if letter == needle and haystack[i-1] != '\\':
                return Span(i, i+1)
        else:
            return False

    @classmethod
    @typed
    def getcaturegroup(cls, string: str, sideeffect: bool=False) -> (tuple, bool):
        string = string.lstrip(' \t')
        if not ':' in string:
            return False
        name = string[:string.index(':')]
        length = len(name)
        isarray = name.endswith('[]')
        if isarray:
            name = name[:-2]
        if name == '':
            cls.capturenumber += int(sideeffect)
            return length, (str(cls.capturenumber -1) if not isarray else str(cls.capturenumber -1) + '[]')
        if not name[0].isalpha() or not all(letter.isalnum() for letter in name[1:]):
            return False
        else:
            return length, name + ('' if not isarray else '[]')

    @classmethod
    @typed
    def shallowsplit(cls, needle: str, opener: str, closer: str, string: str) -> list:
        if cls.countunescaped(opener, string) != cls.countunescaped(closer, string):  # When there aren't as many closing brackets as opening brackets
            raise ValueError('Unbalanced brackets, {!r}'.format(string))  # the string must be invalid, one must be started without being closed

        breakdown = ['']

        while cls.unescapedindex(opener, string):
            openermatch, closermatch = cls.findbalancedpair(opener, closer, string)
            while needle in string[:openermatch.start]:
                needlematch = Span(string[:openermatch.start].index(needle), length=len(needle))
                breakdown[-1] += string[:needlematch.start]
                breakdown.append('')
                string = string[needlematch.end:]
                openermatch += -needlematch.end  # account for changing string itself
                closermatch += -needlematch.end
            breakdown[-1] += string[:closermatch.end]
            string = string[closermatch.end:]

        while needle in string:
            needlematch = Span(string.index(needle), length=len(needle))
            breakdown[-1] += string[:needlematch.start]
            breakdown.append('')
            string = string[needlematch.end:]
        breakdown[-1] += string
        return breakdown


if __name__ == '__main__':
    #print(', '.join("'{}'".format(x) for x in Parser.repeatrange('2-4')))
    #parsed = Parser.parse('[1-3A-z]hello')
    parsed = Parser.parse(r'[#alpha#](:m.{3})(:hello){2}hell(:o)')
    #parsed = Parser.parse('a(hello){2-4}.5\(')
    #parsed = Parser.parse('ak{%2-5}.5\(')
    #parsed = Parser.parse('')
    #print('OUTPUT:', parsed)

    rcprint(parsed)
