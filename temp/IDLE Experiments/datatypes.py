from typeenforcing import typed

class Node:
    value = ''
    negate = False
    branches = []
    reverse = False
    parent = None
    @typed
    def __init__(self, value: str='', negate: bool=False, branches=None, reverse: bool=False):
        self.value = value
        self.branches = branches or []
        self.negate = negate
        self.reverse = reverse

    def __iter__(self):
        yield from self.branches

    def add(self, node, reverse=False):
        assert isinstance(node, Node)
        node.parent = self
        if self.reverse ^ reverse: #wow, xor
            self.branches.insert(0, node)
        else:
            self.branches.append(node)

    def __lshift__(self, node):
        self.add(node)
        return node

    def __rshift__(self, node):
        '''Reverse add the element (to front if not completely reversed)'''
        self.add(node, reverse=True)
        return node

    @typed
    def __getitem__(self, item: int):
        return self.branches[item]

    def __repr__(self):
        return '{}({!r}, {!r}, {!r})'.format(self.__class__.__name__, self.value, self.negate, self.branches)

    @property
    @typed
    def configuration(self) -> dict:
        return {
            'value': self.value,
            'negate': self.negate,
            'branches': list(self.branches),
        }

    def copy(self):
        return self.__class__(**self.configuration)

class Join(Node):
    @typed
    def __init__(self, branches=None):
        self.branches = branches or []

    @typed
    def __repr__(self) -> str:
        return '{}({!r})'.format(self.__class__.__name__, self.branches)

class Tree(Join):

    tree = None
    name = None

    @typed
    def __init__(self, tree=None, branches=None, negate: bool=False, name=None):
        self.branches = branches or []
        self.tree = tree or Join()
        self.negate = negate
        self.name = name

    @typed
    def __repr__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.tree)

    @property
    @typed
    def configuration(self) -> dict:
        configuration = super().configuration
        configuration.pop('value')
        configuration.update({
            'name': self.name,
            'tree': self.tree,
        })
        return configuration

class Span:
    start = 0
    end = 0

    @typed
    def __init__(self, start: (int, tuple)=0, end: int=0, length: int=False):
        if isinstance(start, tuple):
            self.fromtuple(start)
            return
        self.start = start
        self.end = end
        if length and not end:
            self.end = start + length

    @typed
    def fromtuple(self, tuple_: tuple):
        self.__init__(*tuple_)

    def __iter__(self):
        yield from self.bounds

    @property
    @typed
    def bounds(self) -> tuple:
        return self.start, self.end

    @bounds.setter
    @typed
    def bounds(self, tuple_: tuple):
        self.fromtuple(*tuple_)

    @typed
    def __repr__(self) -> str:
        return "{classname}{values}".format(classname=self.__class__.__name__, values=self.bounds)

    @typed
    def __add__(self, change: int):
        return Span(self.start + change, self.end + change)
