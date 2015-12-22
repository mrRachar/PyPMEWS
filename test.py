from main import Matcher, Parser

print('PyPMEWS Tests')

##Basics Test - do the basics work
print('\nBasics Test - do the simple things work')
mypattern = Matcher('he(l){2}o world(:\?)?')            #Create a new matcher with the expression, and store it away in `mypattern` for later use
match = mypattern.match('hello world')                  #See if 'hello world' matches the expression
print('hello world match:', match)                      #Display the hello world match
print('equals hello world:', match == 'hello world')    #Compare if the entire match found is 'helloworld'
match = mypattern.match('hello world?')                 #See if 'hello world?' matches the expression
print('equals hello world?:', match == 'hello world?')  #Compare if the entire match found is 'helloworld?'
print('equals hello world:', match == 'hello world')    #Compare if the entire match found is 'helloworld'
print('hello world groups:', match.groups)              #All the capture groups collected
match = mypattern.match('bright side of life')          #See if 'hello world' matches the expression
print('bright side of life match:', match)              #Display the hello world match

##0.2.1 Test - link capturing with dictionaries
print('\nTest from 0.2.1 - link capturing with dictionaries')
mypattern = Matcher('Hello, (:<name[]:name>)!',
                         links={'name': Parser(r'(:[A-Z]\c+ (\c{2-} )*[A-Z]\c+)')})
match = mypattern.search('I would like to say "Hello, Arthur of the Round Table!".')
print('These two should match:', match, sep='\n')
print('''Match<Hello, (:<name[]:name>)!>('Hello, Arthur of the Round Table!', 'I would like to say "Hello, Arthur of the Round Table!".', {'name': [{'0': 'Arthur of the Round Table'}], '0': 'Arthur of the Round Table'})''')