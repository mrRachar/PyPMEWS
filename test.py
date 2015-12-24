from __init__ import Matcher, Parser
from timeit import timeit

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

#Complicated Number Test - tests most of groups and repeats, by matching it to numbers
print('\nComplicated Number Test - make sure it all works')
print('In cases of invalid tests, it should match a lesser part of the number in most cases')
mypattern = Matcher('-?[1-9](\d{-2}(,\d{3})+|\d*)(\.\d+(e\d+)?)?')
print('42 (valid):', mypattern.match('42').match)
print('4d2 (invalid):', mypattern.match('4d2').match)
print('1701 (valid):', mypattern.match('1701').match)
print('1,701 (valid):', mypattern.match('1,701').match)
print('1,70,1 (invalid):', mypattern.match('1,70,1').match)
print('1,701.112 (valid):', mypattern.match('1,701.112').match)
print('1,701.112e10 (valid):', mypattern.match('1,701.112e10').match)
print('1,701.112e1,0 (invalid):', mypattern.match('1,701.112e1,0').match)




##Speed Test - let's see how fast it is, using the Complicated Number Test
print('\nSpeed Tests - lets see how fast it goes!')
make = """Matcher('-?[1-9](\d{-2}(_\d{3})+|\d*)(\.\d+(e\d+)?)?')"""   #Make the pattern
mypattern = Matcher('-?[1-9](\d{-2}(_\d{3})+|\d*)(\.\d+(e\d+)?)?')
use = """mypattern.match('23_333_211_334_033_211_222.332e10')"""
repeats = 200
print('pattern make: (average of', repeats, 'tests)')
print(timeit(make, setup="from __main__ import Matcher", number=repeats)/repeats)
print('pattern match:')
print(timeit(use, setup="from __main__ import mypattern", number=repeats)/repeats)