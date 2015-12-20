from parsing import Parser  #Parses expressions
from datatypes import *     #Handles data to do with expressions

## TODO # comment and clean

class Match:
    '''A match of an expression against a string

    This contains the match string of what was found,
    the capture groups collected, and the expression
    the match was found by

    If there was no match, an empty one of these will
    be returned by a Matcher, which is falsy'''

    _match = None       #Store of the match as a string or None
    groups = {}         #All the captures from the match
    expression = ''     #The expression the match was found by
    string = ''         #The string the match was found against

    @typed
    def __init__(self, match: (str, type(None))=None, string: str='', expr: str='', groups=None):
        '''A new match of an expression against a string

        With no arguments, creates an empty Match, which
        is falsy

        :param match: str, type(None): The string of the entire match, if none, makes match falsy
        :param string: The string which the match found against
        :param expr: The expression matched against the string
        :param groups: All the capture groups collected by the match
        '''
        #Assign all the parameters to the instance
        self._match = match
        self.groups = groups or {}  #If no group dictionary was given, default to a new one
        self.expression = expr
        self.string = string

    @typed
    def __bool__(self) -> bool:
        '''Return whether a match was made or not

        Uses inner _match attribute, so not equal to match property
        '''
        return bool(self._match is not None)    #Return whether the match is none or not

    @property
    @typed
    def match(self) -> str:
        '''Returns the match string found

        If no match was made, will return an empty string.
        To differentiate between no match, and an empty match,
        see if the match is bool False
        '''
        return self._match or ''

    @match.setter
    @typed
    def match(self, value: (str, type(None))):
        '''Sets the match to the value

        Will set the inner match value, so None may be given

        :param value: str, type(None): the value to set the match to
        '''
        self._match = value #Set the inner match attribute to the parameter given

    def __iadd__(self, other):
        '''Add another match on to this instance

        Will add the remainder of the matches string, and combine the groups found.
        This saves having to do these individually.

        :param other: Match: the other match to add to this one
        '''
        self.match += other.match   #Add the other match on to this one
        self.update(other.groups)   #Merge the two groups, giving precedence to the other's (newer overrides older)
        return self     #Maintain this object, as it is mutable

    @typed
    def __repr__(self) -> str:
        '''Return a representation of the match

        {classname}<{expression}>({match}, {string}, {groups})
        '''
        return '{}<{}>({!r}, {!r}, {!r})'.format(self.__class__.__name__,   #The class name (Match)
                                       self.expression,                     #The expression matched against the string
                                       self._match,                         #The match found (or None if none found)
                                       self.string,                         #The string matched against
                                       self.groups)                         #The groups captured

    def update(self, dictionary):
        '''Update this matches capture groups with another's

        This will also take into account capture collections, and will
        merge them instead of overriding them

        :param dictionary: dict(able): the dictionary to update this matches capture groups by
        '''
        dictionary = dictionary if isinstance(dictionary, dict) else dict(dictionary) #Convert the dictionary to a dict if it isn't
        for key, value in dictionary.items():     #Go through each item in the other's dictionary
            if key.endswith('[]'):              #If it is a collection, but hasn't been turned into one yet
                key = key[:-2]                  # extract the name,
                if key not in self.groups:      # see if this instance already has it
                    self.groups[key] = []       # if not, add a new list there
                self.groups[key].append(value)  # add item to the list
            elif isinstance(value, list):   #If it is a collection of values,
                if key not in self.groups:  # if we don't have the collection yet
                    self.groups[key] = []   # make a new one under that name
                self.groups[key] += value   # and join them eitherway
            else:
                self.groups[key] = value    #If it just a normal value, add it whether it overrides or not


class Matcher:
    '''A matcher with a stored expression to match against strings

    This takes an expression, breaks it down into a tree, and then
    matches that against strings given, returning matches
    '''
    __expression = None     #The private underlying expression, never to be directly changed so always to be a direct representation of the tree
    tree = None             #The tree matched against strings
    def __init__(self, expr: str):
        '''Create a new matcher from the expression

        Sets the expression to the instance property, which is then
        automatically broken down into a tree by the parser, and
        both are stored

        To be used to match against strings
        '''
        self.expression = expr  #Set the expression to the property, so it will automatically be parsed and set to the tree

    @property
    @typed
    def expression(self) -> str:
        '''The expression the matcher matches'''
        return self.__expression #Return the private instance expression

    @expression.setter
    @typed
    def expression(self, expr: str):
        '''Set the expression and the tree

        Sets the expression to the instance attribute, and then breaks it
        down into a tree using the parser and stores the tree aswell

        :param expr: str: the expression to set and breakdown into the tree
        '''
        self.__expression = expr
        self.tree = Parser(expr)

    @typed
    def match(self, string: str) -> Match:
        '''Match the expression to the string exactly, from the start

        Will compare the tree to the string given, returning a Match
        instance, which will be falsy if no match is made. It doesn't
        necessarily have to match to the end of the string

        :param string: str: the string to match against the expression
        '''
        match = self.compare(string)            #Compare the string to the expression
        match.expression = self.__expression    #Set the match up with the expression,
        match.string = string                   # and the given string
        return match    #Return the new match, be it falsy or not

    @typed
    def search(self, string) -> Match:
        '''NotImplemented fully'''
        for substring in (string[i:] for i in range(len(string))):
            match = self.compare(substring)
            if match:
                match.expression = self.__expression
                return match
        else:
            return Match(expr=self.__expression)

    @typed
    def negativecompare(self, string: str, node=None) -> Match:
        '''Compare the string against the node tree segment,
        making sure they cannot match

        This will go through and check if there is not match, and then
        make sure all the branches don't match, and only then will it pass
        on to the first branch and continue on through the branches until
        a complete path is found where there in no match.

        :param string: str: the string to negatively compare against
        :param node: the node to start with
        '''
        letter = string[0]              #Set the letter to compare to be the first of the string
        node = node or self.tree.tree   #If no node was given, default to the matcher's main tree node (never used in this method)

        if not isinstance(node, Join) and self.equals(letter, node):    #If it isn't a join and there letter equals the node,
            return Match()                                              # they mustn't not equal, so return there wasn't a match

        if not node.branches:                                           #If this is the end of the tree segment
            return Match(letter if not isinstance(node, Join) else '')  # only see if it's a join or not, and return the relevant string in a Match

        for branch in node.branches:                                            #Seeing as it has got branches, go through them,
            if not isinstance(branch, Join) and self.equals(letter, branch):    # and if it does match, a bad thing,
                return Match()                                                  # return that they don't not match

        for branch in node.branches:        #Now we know all the branches are valid, no possibility of a match,
            branchmatch = self.negativecompare(string[int(not isinstance(node, Join)):], branch)    # we can negatively compare this branch
            if not branchmatch:                                             #If it doesn't negatively match,
                continue                                                    # move on
            match = Match(letter if not isinstance(node, Join) else '')     #Make a new match of the relevant letter,
            match += branchmatch                                            # add on the branches match to it,
            return match                                                    # and return the match
        else:               #If none of the branches negatively matched,
            return Match()  # return there wasn't a match


    @typed
    def compare(self, string: str, node=None) -> Match:
        '''Compare the string against the node tree segment, seeing if there
        is a way they could be equal.

        Makes sure this node equals the first letter, and then tries to match
        it with branches, until it finds one that matches.

        Will return an empty, falsy Match if no match made

        :param string: str: the string to compare against
        :param node: Node, type(None): the node to start at
        '''
        letter = string[0]              #Set the letter to be compared against to be the first of the string
        node = node or self.tree.tree   #If there was no node given, default to the node at the top of the tree
        match = Match()                 #Get a match ready, so that later there will be a match, no matter what

        if isinstance(node, Tree):                              #If we've got a tree
            if node.negate:                                     #Check if it is negated, and if so
                match = self.negativecompare(string, node.tree) # negatively compare it
            else:                                           #If it is not negated,
                match = self.compare(string, node.tree)     # just compare it normally
            if not match:           #When no match is made
                return match        # return this no match Match
            else:                                       #When we have a match
                string = string[len(match.match):]      #get rid of the string up till there
                if not string:                                      #If that leaves the string empty
                    return match if not node.branches else Match()  # return the match collected, unless the tree has more, so no match was made
                letter = string[0]                          #Reset the letter to the beginning of the new string
                if node.name:                               #If the tree has a name,
                    match.update({node.name: match.match})  # add the captured text to it

        if self.equals(letter, node):                      #When a match has been made already, or the letter and the node's value are equal
            if not string[1:] and not isinstance(node, Join):           #If the string has run out,
                return Match(letter) if not node.branches else Match()  # return the match so far, unless the tree has more, so no match was made
            elif node.branches:                 #If it has branches,
                for branch in node.branches:    # go through each branch
                    #Compare the string following this letter, except that Joins don't have any value so check this letter again if it is a Join
                    branchmatch = self.compare(string[int(not isinstance(node, Join)):], branch)
                    if not branchmatch:     #If not a match was made,
                        continue            # then check the next branch
                    match.match += letter if not isinstance(node, Join) else '' #Add the current letter to the match if we haven't a join
                    match += branchmatch    #Add the match of the branch onto this match,
                    return match            # and return it all
                else:               #If there was never a match made in the branches
                    return Match()  # return an empty match
            else:                                                           #If there are no branches,
                return Match(letter if not isinstance(node, Join) else '')  # return what we got
        else:               #If it isn't equal and no match was made earlier,
            return Match()  # then we haven't got a match

    @typed
    def equals(self, letter: str, node: Node) -> bool:
        '''Sees if the letter could be equal to the node

        Will check if they are directly equal, but also if some other value such as
        'any' or 'space' or a range is set to the nodes value, will see if the letter
        satisfies the nodes value

        If it is a join, will automatically return true as Joins (and Trees) have no value

        :param letter: str: the letter to compare
        :param node: Node: the node whose value to compare
        '''
        if isinstance(node, Join):  #If we have a Join
            return True             # return True as they have no real value
        if len(node.value) > 1:         #If the nodes value isn't a simple letter, do further testing
            if node.value == 'any':                                         #If it can be anything
                return (node.value != '\n') if not node.negate else False   # check it isn't a newline 'cause I don't think they count
            elif node.value[1] == '-':                                                      #If it has a line in the middle,
                result = ord(letter) in range(ord(node.value[0]), ord(node.value[2]) + 1)   # see if the letter is in the ascii range given
                if node.negate:         #If it is negated,
                    return not result   # negate the result
                return result           #Otherwise, don't, just don't
            elif node.value in ['alphanum', 'alpha', 'space']:  #If it is a special name
                result = {
                    'alphanum': lambda x: ord('A') <= ord(x) <= ord('Z') or ord('a') <= ord(x) <= ord('z') or ord('0') <= ord(x) <= ord('9'),
                    'alpha': lambda x: ord('A') <= ord(x) <= ord('Z') or ord('a') <= ord(x) <= ord('z'),
                    'space': lambda x: x in (' ', '\t'),
                }[node.value](letter)   #Get the comparision function to see if the letter satisfies the conditions place of it.
                if node.negate:         #If you must,
                    return not result   # negate it
                return result           #Only if you must, though
        if node.negate:                     #So it isn't special, see if we still have to negate it
            return node.value != letter     #Return whether they are not equal
        return node.value == letter     #No negation, so return if it is just some simple equals thing

## TESTS ##

#a = Matcher('a{%3-5}aa')
a = Matcher(r'\d(word[]:m.{3})(word[]:hello){2}hello')
#a = Matcher('[^efgijk](blur:[^aiouy]ll)o,\s[wd]orl[^t]')
print('#tree', a.tree)
print(a.match('9mnnehellohellohelloj'))
#print(a.match('9mnnehellohellohello'))
#m = Matcher('kkk(e){4}')
#print(m.match('kkkeeeee'))
#timed.timeit(a.match)('namehellohellohello', timed_repeats=10)
#timed.timeit(re.match)(r'(name)(hello){2}hello', 'namehellohellohello', timed_repeats=10)
#print(a.search('hel{1-2}o'))
