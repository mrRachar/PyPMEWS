from parsing import Parser
from datatypes import *

DEBUG = False

## TODO # change capturing
##          - who will rid me of this turbulent priest
##          - get rid of the last regex statement from the parser
##          - allow for unnamed captures (auto-enumerating)
## TODO # comment and clean


class Match:
    _match = None
    groups = {}
    expression = ''

    @typed
    def __init__(self, match=None, string: str='', expr: str='', groups=None):
        self._match = match
        self.groups = groups or {}
        self.expression = expr
        self.string = string

    @typed
    def __bool__(self) -> bool:
        return bool(self._match is not None)

    @property
    @typed
    def match(self) -> str:
        return self._match or ''

    @match.setter
    @typed
    def match(self, value: (str, None)):
        self._match = value

    def __iadd__(self, other):
        self._match += other.match
        self.update(other.groups)
        return self

    def __repr__(self):
        return '{}[{}]({!r}, {!r}, {!r})'.format(self.__class__.__name__,
                                       self.expression,
                                       self._match,
                                       self.string,
                                       self.groups)

    def update(self, dictionary):
        dictionary = dictionary if isinstance(dictionary, dict) else dict(dictionary)
        for key, value in dict(dictionary).items():
            if key.endswith('[]'):
                key = key[:-2]
                if key not in self.groups:
                    self.groups[key] = []
                self.groups[key].append(value)
            elif isinstance(value, list):
                if key not in self.groups:
                    self.groups[key] = []
                self.groups[key] += value
            else:
                self.groups[key] = value


class Matcher:
    __expression = None
    tree = None
    def __init__(self, expr: str):
        self.expression = expr

    @property
    def expression(self):
        return self.__expression

    @expression.setter
    @typed
    def expression(self, expr: str):
        self.__expression = expr
        self.tree = Parser(expr)

    @typed
    def match(self, string) -> Match:
        match = self.compare(string)
        match.expression = self.__expression
        match.string = string
        return match

    @typed
    def search(self, string) -> Match:
        for substring in (string[i:] for i in range(len(string))):
            match = self.compare(substring)
            if match:
                match.expression = self.__expression
                return match
        else:
            return Match(expr=self.__expression)

    def negativecompare(self, string: str, node=None) -> Match: ##TEST THIS OUT
        letter = string[0]
        node = node or self.tree.tree

        if not isinstance(node, Join) and self.equals(letter, node):
            return Match()

        if not node.branches:
            return Match(letter if not isinstance(node, Join) else '')

        for branch in node.branches:
            if not isinstance(branch, Join) and self.equals(letter, branch):
                return Match()

        for branch in node.branches:
            branchmatch = self.negativecompare(string[int(not isinstance(node, Join)):], branch)
            if not branchmatch:
                continue
            match = Match(letter if not isinstance(node, Join) else '')
            match += branchmatch
            return match

        else:
            return Match()


    @typed
    def compare(self, string: str, node=None) -> Match:
        letter = string[0]
        match = Match()
        node = node or self.tree.tree

        if isinstance(node, Tree):
            if node.negate:
                match = self.negativecompare(string, node.tree)
            else:
                match = self.compare(string, node.tree)
            if not match:
                return match
            else:
                string = string[len(match.match):]
                if not string:
                    return match if not node.branches else Match()
                letter = string[0]
                if node.name:
                    match.update({node.name: match.match})

        if match or self.equals(letter, node):
            if not string[1:] and not isinstance(node, Join):
                return Match(letter) if not node.branches else Match()
            elif node.branches:
                for branch in node.branches:
                    branchmatch = self.compare(string[int(not isinstance(node, Join)):], branch) #don't progress if we have a join
                    if not branchmatch:
                        continue
                    match.match += letter if not isinstance(node, Join) else ''
                    match += branchmatch
                    return match
                else:
                    return Match()
            else:
                return Match(letter if not isinstance(node, Join) else '')
        else:
            return Match()

    @typed
    def equals(self, letter: str, node: Node):
        if isinstance(node, Join):
            return True
        if len(node.value) > 1:
            if node.value == 'any':
                return (node.value != '\n') if not node.negate else False
            elif node.value[1] == '-':
                result = ord(letter) in range(ord(node.value[0]), ord(node.value[2]) + 1)
                if node.negate:
                    return not result
                return result
            elif node.value in ['alphanum', 'alpha', 'space']:
                result = {
                    'alphanum': lambda x: ord('A') <= ord(x) <= ord('Z') or ord('a') <= ord(x) <= ord('z') or ord('0') <= ord(x) <= ord('9'),
                    'alpha': lambda x: ord('A') <= ord(x) <= ord('Z') or ord('a') <= ord(x) <= ord('z'),
                    'space': lambda x: x in (' ', '\t'),
                }[node.value](letter)
                if node.negate:
                    return not result
                return result
        if node.negate:
            return node.value != letter
        return node.value == letter

## TESTS ##

#a = Matcher('a{%3-5}aa')
#a = Matcher(r'\d(word[]:m.{3})(word[]:hello){2}hello')
a = Matcher('[^efgijk](blur:[^aiouy]ll)o,\s[wd]orl[^t]')
print('#tree', a.tree)
print(a.match('hello, world'))
#print(a.match('9mnnehellohellohello'))
#m = Matcher('kkk(e){4}')
#print(m.match('kkkeeeee'))
#timed.timeit(a.match)('namehellohellohello', timed_repeats=10)
#timed.timeit(re.match)(r'(name)(hello){2}hello', 'namehellohellohello', timed_repeats=10)
#print(a.search('hel{1-2}o'))
