from typeenforcing import typed

class Node:
    """A part of a tree, which will match letters

    It has a value, and branches of other nodes, and is used as part of a tree,
    so strings can be matched against the expression, by comparing them to nodes
    """

    value = ''          #The value of the node
    negate = False      #Whether the node is or isn't negated
    branches = []       #The nodes this node is connected to
    reverse = False     #Whether the branches should be reverse-checked
    parent = None       #The (main) node this is connected to
    id = None           #To identify clones
    autoid = 0          #Universal ID number

    @typed
    def __init__(self, value: str='', branches=None, *, negate: bool=False, reverse: bool=False, id=None):
        """Create a new Node, with the value given

        :param value: str: the value of the node
        :param negate: bool: whether the node's value should be negatively compared
        :param branches: list: default branches that this node should use
        :param reverse:  bool: whether branches should be dealt with in reverse (for greedlessness)
        """
        #Assign all the parameters to the instance
        self.value = value
        self.branches = branches or []  #If no branch list was given, create a new list
        self.negate = negate
        self.reverse = reverse
        self.id = id or self.__class__.autoid
        self.__class__.autoid += 1

    def __iter__(self):
        """Iterate through all the branches that the node has

        Yields from the instances branches list
        """
        yield from self.branches    #Return all the branches from the branch list

    def add(self, node, *, reverse=False):
        """Add a branch to this node

        The node will be added the list of branches. If reverse is specified,
        then it will be added at the front. If reverse is specified for the
        instance, then it will be added at the opposite end than normal

        :param node: Node: the Node to add as a branches
        :param reverse: whether to add it at the opposite end, normally the front
        """
        assert isinstance(node, Node), 'Only a node may be added as a branch' #Make sure that we're adding a node as a branch
        node.parent = self #Make the node's parent this instance
        if self.reverse ^ reverse:          #If it is in reverse mode, or the instance is, but not both, because they should cancel out,
            self.branches.insert(0, node)   # add it to the front of the branch list
        else:                               #If however the was no reverse specified, or in the case of a double reverse,
            self.branches.append(node)      # append the node as the last branch

    def __lshift__(self, node):
        """Add a node as a branch

        This behaves like .add, except provides native syntax, and also returns the
        node afterwards.

        Commonly used in 'i' form:
            node <<= branch
        """
        self.add(node)  #Add the node as a branch
        return node     #Return this node (especially for 'i' form, for further use)

    def __rshift__(self, node):
        """Add a node as a branch at the opposite than normal end

        This is the negative form or <<, behaving like .add(reverse=True) except providing
        native syntax, and also returning the node afterwards

        Commonly used in the 'i' form:
            node >>= branch
        """
        self.add(node, reverse=True)    #Add the node as a branch in reverse
        return node                     #Return this node (especially for 'i' form, for further use)

    @typed
    def __getitem__(self, item: int):
        """Return the item of the given branch"""
        return self.branches[item]

    @typed
    def __repr__(self) -> str:
        """Represent the node, in initialisation form"""
        #Format a string with all the initialisation arguments value
        return '{}({!r}, {!r}, negate={!r}, reverse={!r}, id={!r})'.format(
            self.__class__.__name__,
            self.value,
            self.branches,
            self.negate,
            self.reverse,
            self.id
        )

    @typed
    def __mod__(self, other) -> bool:
        """Compare two nodes, to see if they have the same id"""
        try:
            #If both have ids and they are the same
            return self.id is not None and other.id is not None and self.id == other.id
        except:
            return False    #If one wasn't a node, just return False

    @typed
    def __eq__(self, letter: str) -> bool:
        """Sees if the node could be equal to the letter

        Will check if they are directly equal, but also if some other value such as
        'any' or 'space' or a range is set to the nodes value, will see if the letter
        satisfies the nodes value

        :param letter: str: the letter to compare
        :param node: Node: the node whose value to compare
        """
        if len(self.value) > 1:         #If the nodes value isn't a simple letter, do further testing
            if self.value == 'any':                                         #If it can be anything,
                return (self.value != '\n') if not self.negate else False   # check it isn't a newline 'cause I don't think they count
            elif self.value[1] == '-':                                                      #If it has a line in the middle,
                result = ord(letter) in range(ord(self.value[0]), ord(self.value[2]) + 1)   # see if the letter is in the ascii range given
                if self.negate:         #If it is negated,
                    return not result   # negate the result
                return result           #Otherwise, don't, just don't
            elif self.value in ['alphanum', 'alpha', 'space', 'breaker']:  #If it is a special name
                result = {
                    'alphanum': lambda x: ord('A') <= ord(x) <= ord('Z') or ord('a') <= ord(x) <= ord('z') or ord('0') <= ord(x) <= ord('9'),
                    'alpha': lambda x: ord('A') <= ord(x) <= ord('Z') or ord('a') <= ord(x) <= ord('z'),
                    'space': lambda x: x in ' \t',
                    'breaker': lambda x: x in ' \n\t',
                }[self.value](letter)   #Get the comparison function to see if the letter satisfies the conditions place of it.
                if self.negate:         #If you must,
                    return not result   # negate it
                return result           #Only if you must, though
        if self.negate:                     #So it isn't special, see if we still have to negate it
            return self.value != letter     #Return whether they are not equal
        return self.value == letter     #No negation, so return if it is just some simple equals thing

    @property
    @typed
    def configuration(self) -> dict:
        """Return the configuration of this node"""
        return {
            'value': self.value,
            'negate': self.negate,
            'branches': list(self.branches),
            'id': self.id
        }

    def copy(self):
        """Create a duplicate of this node, using all the configurations of it"""
        return self.__class__(**self.configuration) #Initialise a new instance, with all the same parameters, and return it

class Join(Node):
    """An empty node, used to connect branches back together"""
    @typed
    def __init__(self, branches=None, id=None):
        """Create a new Join, with the given branches"""
        self.branches = branches or [] #Set the instance attribute to the given branch, unless None was, then create a new list of branches
        self.id = id or self.__class__.autoid
        self.__class__.autoid += 1

    @typed
    def __repr__(self) -> str:
        """Represent the node, in initialisation form"""
        #Format a string with all the initialisation arguments
        return '{}({!r}, id={!r})'.format(self.__class__.__name__, self.branches, self.id)

    @typed
    def __eq__(self, string: str) -> bool:
        """Joins are always 'equal' to a letter, but the letter should be tested against
         the next node in the implementation"""
        return True     #Joins are always equals to a string, as they have no value

class Tree(Join):
    """A tree of nodes, starting with one which then has branches
    
    A tree can also be treated like a Node, and is a Join, as it itself
    has no value in that expression level. It is tested, and then the
    match, if any, should be removed from the string, and the tree treated
    like any Join thenceforth
    """
    tree = None         #The first node of the tree
    name = None         #The name of the capture group, if any

    @typed
    def __init__(self, tree=None,branches=None, *, negate: bool=False, name=None, id=None):
        """Create a new tree, with the given Node (and branches to start), branches
        negation, and capture group name"""
        super().__init__(branches, id=id)   #Call the superclass, Join, with the branches to set them up, and the id argument
        #Assign the parameters to the instance
        self.tree = tree or Join()          #Create an empty join to add to later if no node was given to start with
        self.negate = negate
        self.name = name

    @typed
    def __repr__(self) -> str:
        """Display the tree of nodes"""
        #Return the class name, and the tree of nodes in a string tree=None,branches=None, *, negate: bool=False, name=None, id=None)
        return '{}({!r}, {!r}, negate={!r}, name={!r}, id={!r})'.format(
            self.__class__.__name__,
            self.tree,
            self.branches,
            self.negate,
            self.name,
            self.id
        )

    @property
    @typed
    def configuration(self) -> dict:
        """Return the configuration of this node"""
        configuration = super().configuration   #Start with Node's configuration
        configuration.pop('value')              #Get rid of the value, trees have no value
        configuration.update({                  #Add,
            'name': self.name,                  # the capture group name
            'tree': self.tree,                  # and the tree itself
        })
        return configuration                    #Return the configuration of the instance

class Link(Join):
    """A placeholder referring to another expression, a subclass of Join

    This stores the name of another expression, and when reaches, should cause
    the matcher to treat the other expression like a subtree. It like trees can
    have capture groups
    """
    name = None
    _link = ''
    def __init__(self, link: str, branches=None, *, negate=False, name=None, id=None):
        """Create a new link, with the location of the expression to link to

        Instantiate the new link, which the links location obligatory, and
        optional branches, negation and name, like a Tree
        """
        super().__init__(branches, id=id)   #Call the superclass, Join, with the branches, and id, to set them up
        #Assign the parameters to the instance
        self.name = name
        self.negate = negate
        self.link = link

    def __repr__(self) -> str:
        """Display the link location, and the branches"""
        return '{}({}, {}, negate={}, name={}, id={})'.format(  #Format a string with a replica of initialisation, including:
            self.__class__.__name__,                            # the class name,
            self.link,                                          # the link to the expression
            self.branches,                                      # branches of this node
            self.negate,                                        # negation of the expression (tree)
            self.name,                                          # the name of the capture group, (or None),
            self.id,                                            # the unique (except clones) id of the node
        )

    @property
    @typed
    def link(self) -> str:
        """Return the link of this Link

        This is protected behind a property, in order to prevent it being
        set to empty
        """
        return self._link   #Return the hidden link attribute

    @link.setter
    @typed
    def link(self, location: str):
        '''Set the link of this Link

        It cannot be set to empty, doing so will raise an Assertion Error
        '''
        assert location != '', "A link location must be provided"   #Make sure a valid location is given
        self._link = location                                       #Set the link to that location

    @property
    @typed
    def configuration(self) -> dict:
        """Return the configuration of this node"""
        configuration = super().configuration   #Start with Node's configuration
        configuration.pop('value')              #Get rid of the value, links have no value
        configuration.update({                  #Add,
            'name': self.name,                  # the capture group name
            'link': self.link,                  # and the link where this goes
        })
        return configuration                    #Return the configuration of the instance



class Span:
    """A section of a text, with a start and an end

    Equivalent of slice with more functionality
    """
    start = 0   #The start of the span
    end = 0     #The end of the span

    @typed
    def __init__(self, start: (int, tuple)=0, end: int=0, length: int=0):
        """Create a new span, from the start to the end

        If a length is given, it will set the end to that far from the start
        """
        if isinstance(start, tuple):    #If we've been given a tuple,
            self.fromtuple(start)       # use it to built the span
            return
        #Set the instance attributes with the parameters
        self.start = start
        self.end = end
        if length:                      #If a length was given,
            self.end = start + length   # set the end the length from the start

    @typed
    def fromtuple(self, tuple_: tuple):
        """Set the span from a tuple"""
        self.__init__(*tuple_)  #Unpack the tuple, and use init to set values

    def __iter__(self):
        '''Go through each bound, the start and then the end'''
        yield from self.bounds  #Iterate through the tuple of the bounds (start, end)

    @property
    @typed
    def bounds(self) -> tuple:
        '''Return a tuple of the start point and the end'''
        return self.start, self.end

    @bounds.setter
    @typed
    def bounds(self, tuple_: tuple):
        '''Reassign the bounds with a tuple'''
        self.fromtuple(*tuple_)     #Use the tuple to get new bounds'''

    @typed
    def __repr__(self) -> str:
        return "{classname}{values!r}".format(classname=self.__class__.__name__, values=self.bounds)

    @typed
    def __add__(self, change: int):
        '''Offset the span, at both ends, by a integer'''
        return Span(self.start + change, self.end + change)