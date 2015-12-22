from parsing import Parser, rcprint     #Parses expressions, rcprint for debugging only
from datatypes import *                 #Handles data to do with expressions

#TODO end problem came back... in some weird repeat cases (*, + to end only)

class Match:
    """A match of an expression against a string

    This contains the match string of what was found,
    the capture groups collected, and the expression
    the match was found by

    If there was no match, an empty one of these will
    be returned by a Matcher, which is falsy
    """
    _match = None       #Store of the match as a string or None
    groups = {}         #All the captures from the match
    expression = ''     #The expression the match was found by
    string = ''         #The string the match was found against

    @typed
    def __init__(self, match: (str, type(None))=None, string: str='', expr: str='', groups=None):
        """A new match of an expression against a string

        With no arguments, creates an empty Match, which
        is falsy

        :param match: str, type(None): The string of the entire match, if none, makes match falsy
        :param string: The string which the match found against
        :param expr: The expression matched against the string
        :param groups: All the capture groups collected by the match
        """
        #Assign all the parameters to the instance
        self._match = match
        self.groups = groups or {}  #If no group dictionary was given, default to a new one
        self.expression = expr
        self.string = string

    @typed
    def __bool__(self) -> bool:
        """Return whether a match was made or not

        Uses inner _match attribute, so not equal to match property
        """
        return bool(self._match is not None)    #Return whether the match is none or not

    @property
    @typed
    def match(self) -> str:
        """Returns the match string found

        If no match was made, will return an empty string.
        To differentiate between no match, and an empty match,
        see if the match is bool False
        """
        return self._match or ''

    @match.setter
    @typed
    def match(self, value: (str, type(None))):
        """Sets the match to the value

        Will set the inner match value, so None may be given

        :param value: str, type(None): the value to set the match to
        """
        self._match = value #Set the inner match attribute to the parameter given

    def __iadd__(self, other):
        """Add another match on to this instance

        Will add the remainder of the matches string, and combine the groups found.
        This saves having to do these individually.

        :param other: Match: the other match to add to this one
        """
        self.match += other.match   #Add the other match on to this one
        self.update(other.groups)   #Merge the two groups, giving precedence to the other's (newer overrides older)
        return self     #Maintain this object, as it is mutable

    @typed
    def __repr__(self) -> str:
        """Return a representation of the match

        {classname}<{expression}>({match}, {string}, {groups})
        """
        return '{}<{}>({!r}, {!r}, {!r})'.format(self.__class__.__name__,   #The class name (Match)
                                       self.expression,                     #The expression matched against the string
                                       self._match,                         #The match found (or None if none found)
                                       self.string,                         #The string matched against
                                       self.groups)                         #The groups captured

    def update(self, dictionary):
        """Update this matches capture groups with another's

        This will also take into account capture collections, and will
        merge them instead of overriding them

        :param dictionary: dict(able): the dictionary to update this matches capture groups by
        """
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

    @typed
    def __eq__(self, other: (str, type(None))) -> bool:
        """Is the string equal to the whole match

        Compares the string to the whole match, returning equal if they are
        the same, and the match is not False (empty). If equated to None, will
        return whether the match is empty
        """
        if not self:                #If this Match is empty,
            return other is None    # only return True if equated with empty
        elif other is None:     #If the other is empty,
            return False        # return False, as this is not
        return self._match == other     #Seeing as they're both strings, see if they are equal


class Matcher:
    """A matcher with a stored expression to match against strings

    This takes an expression, breaks it down into a tree, and then
    matches that against strings given, returning matches
    """
    __expression = None     #The private underlying expression, never to be directly changed so always to be a direct representation of the tree
    tree = None             #The tree matched against strings
    links = {}
    def __init__(self, expr: str, *, links=None):
        """Create a new matcher from the expression

        Sets the expression to the instance property, which is then
        automatically broken down into a tree by the parser, and
        both are stored

        To be used to match against strings

        :param expr: str: the expression to be broken into a tree and compared to strings
        :param links: dict, LinksCollection: the dictionary of links to use
        """
        self.expression = expr      #Set the expression to the property, so it will automatically be parsed and set to the tree
        self.links = links or {}    #Set the links to the links provided, otherwise make a new dictionary of them

    @property
    @typed
    def expression(self) -> str:
        """The expression the matcher matches"""
        return self.__expression #Return the private instance expression

    @expression.setter
    @typed
    def expression(self, expr: str):
        """Set the expression and the tree

        Sets the expression to the instance attribute, and then breaks it
        down into a tree using the parser and stores the tree aswell

        :param expr: str: the expression to set and breakdown into the tree
        """
        self.__expression = expr
        self.tree = Parser(expr)

    @typed
    def match(self, string: str) -> Match:
        """Match the expression to the string exactly, from the start

        Will compare the tree to the string given, returning a Match
        instance, which will be falsy if no match is made. It doesn't
        necessarily have to match to the end of the string

        :param string: str: the string to match against the expression
        """
        match = self.compare(string)            #Compare the string to the expression
        match.expression = self.__expression    #Set the match up with the expression,
        match.string = string                   # and the given string
        return match    #Return the new match, be it falsy or not

    @typed
    def search(self, string) -> Match:
        """Iteratively search through the string until a match is found

        Will start at the beginning of the string, and try and make a match.
        It will continue starting at the next letter of the string, until a
        match is made. If no match is made by the end, a empty match will
        be returned

        :param string: str: the string to match against the expression
        """
        #Go through the substring of i 'til the end up til one short of the length of the string
        for substring in (string[i:] for i in range(len(string)-1)):
            match = self.compare(substring) #Try and make a match
            if match:                                   #If the match was successful
                match.expression = self.__expression    #Set the match up with the expression,
                match.string = string                   # and the given string
                return match                            #Return the match found
        else:
            #If no match was made, return an empty match object, still with match information
            return Match(expr=self.__expression, string=string)

    @typed
    def negativecompare(self, string: str, node=None) -> Match:
        """Compare the string against the node tree segment,
        making sure they cannot match

        This will go through and check if there is not match, and then
        make sure all the branches don't match, and only then will it pass
        on to the first branch and continue on through the branches until
        a complete path is found where there in no match.

        :param string: str: the string to negatively compare against
        :param node: the node to start with
        """
        letter = string[0]              #Set the letter to compare to be the first of the string
        node = node or self.tree.tree   #If no node was given, default to the matcher's main tree node (never used in this method)

        if not isinstance(node, Join) and letter == node:    #If it isn't a join and there letter equals the node,
            return Match()                                              # they mustn't not equal, so return there wasn't a match

        if not node.branches:                                           #If this is the end of the tree segment
            return Match(letter if not isinstance(node, Join) else '')  # only see if it's a join or not, and return the relevant string in a Match

        for branch in node:                                                     #Seeing as it has got branches, go through them,
            if not isinstance(branch, Join) and letter == branch:               # and if it does match, a bad thing,
                return Match()                                                  # return that they don't not match

        for branch in node:         #Now we know all the branches are valid, no possibility of a match,
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
        """Compare the string against the node tree segment, seeing if there
        is a way they could be equal.

        Makes sure this node equals the first letter, and then tries to match
        it with branches, until it finds one that matches.

        Will return an empty, falsy Match if no match made

        :param string: str: the string to compare against
        :param node: Node, type(None): the node to start at
        """
        node = node or self.tree.tree   #If there was no node given, default to the node at the top of the tree
        if string == '':    #If we've run out of string
            #Check to see if the tree is not exhausted (there are more branches, and not just one empty Join at most)
            if node.branches and not (len(node.branches) == 1 and type(node.branches[0]) is Join and not node.branches[0].branches):
                return Match()      #Then the tree is not yet exhausted, so there wasn't a match with the entire tree
            else:                   #If the tree has been exhausted as well as the string, the match is successful,
                return Match('')    # but with no letter, so return a non-falsy empty string match is returned
        letter = string[0]              #Set the letter to be compared against to be the first of the string
        match = Match()                 #Get a match ready, so that later there will be a match, no matter what

        if isinstance(node, (Tree, Link)):          #If we've got a tree or link
            if isinstance(node, Link):              #If it's a link,
                tree = self.links[node.link].tree   # make the tree the link's list at that index Tree's tree
            else:                                   #Otherwise, just like normal,
                tree = node.tree                    # use the (Tree) node's tree
            if node.negate:                                 #Check if it is negated, and if so
                match = self.negativecompare(string, tree)  # negatively compare it
            else:                                       #If it is not negated,
                match = self.compare(string, tree)      # just compare it normally
            if not match:           #When no match is made,
                return match        # return this no match Match
            else:                                       #When we have a match
                string = string[len(match.match):]      #get rid of the string up till there
                if node.name:
                    if isinstance(node, Link):          #If the link has a name
                        match.groups, linkgroups = {}, match.groups     #Reset the match groups, storing them
                        match.update({node.name: linkgroups})           # to be added under the link's name
                    else:                                       #If the tree has a name,
                        match.update({node.name: match.match})  # add the captured text to it
                if not string:      #If that leaves the string empty, return
                    #If there are branches, and none of them are dead ends
                    if node.branches and not any(type(branch) is Join and not branch.branches for branch in node):
                        return Match()  #Then the tree is not yet exhausted, so there wasn't a match
                    return match    #Seeing as the tree is exhausted, we can return the match we have made
                letter = string[0]                          #Reset the letter to the beginning of the new string

        if letter == node:                      #When a match has been made already, or the letter and the node's value are equal
            if node.branches:                   #If it has branches,
                for branch in node:             # go through each branch
                    #Compare the string following this letter, except that Joins don't have any value so check this letter again if it is a Join
                    branchmatch = self.compare(string[int(not isinstance(node, Join)):], branch)
                    if not branchmatch:     #If not a match was made,
                        continue            # then check the next branch
                    match.match += letter if not isinstance(node, Join) else '' #Add the current letter to the match if we haven't a join
                    match += branchmatch    #Add the match of the branch onto this match,
                    return match            # and return it all
                else:               #If there was never a match made in the branches
                    return match    # return an empty match #todo make sure returning not new instances is ok
            else:                                                               #If there are no branches,
                match += Match(letter if not isinstance(node, Join) else '')    # add the last letter on and,
                return match                                                    # return what we got
        else:               #If it isn't equal and no match was made earlier,
            return match    # then we haven't got a match

'''
## TESTS ## Run these to check things

#a = Matcher('a{%3-5}aa')
#a = Matcher('Hello, ([A-Z]\c+ (\c{2-} )*[A-Z]\c+)', links={'name': Parser(r'[A-Z]\c+ (\c{2-} )*[A-Z]\c+')})
#a = Matcher(r'[A-Z]\c+ (\c{2-} )*[A-Z]\c+')
#print(a.match('Hello, Matthew Ross Campbell dRachar'))
#main#a = Matcher(r'\d(word[]:m.{3})(word[]:hello|world){2}hello')
#a = Matcher('[^efgijk](blur:[^aiouy]ll)o,\s[wd]orl[^t]')
rcprint(a.tree)
#main#print(a.match('9mnnehelloworldhelloj'))
#print(a.match('9mnnehellohellohello'))
#m = Matcher('kk(e){4}')
#print(m.match('kkeeeee'))
#timed.timeit(a.match)('namehellohellohello', timed_repeats=10)
#timed.timeit(re.match)(r'(name)(hello){2}hello', 'namehellohellohello', timed_repeats=10)
#print(a.search('hel{1-2}o'))
rcprint(a.links['name'].tree)
'''