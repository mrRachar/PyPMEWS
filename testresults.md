## Test Output
When running `test.py` for the latest version, you should see exactly this (well, except for the font might be different).
```
PyPMEWS Tests

Basics Test - do the simple things work
hello world match: Match<he(l){2}o world(:\?)?>('hello world', 'hello world', {})
equals hello world: True
equals hello world?: True
equals hello world: False
hello world groups: {'0': '?'}
bright side of life match: Match<he(l){2}o world(:\?)?>(None, 'bright side of life', {})

Test from 0.2.1 - link capturing with dictionaries
These two should match:
Match<Hello, (:<name[]:name>)!>('Hello, Arthur of the Round Table!', 'I would like to say "Hello, Arthur of the Round Table!".', {'name': [{'0': 'Arthur of the Round Table'}], '0': 'Arthur of the Round Table'})
Match<Hello, (:<name[]:name>)!>('Hello, Arthur of the Round Table!', 'I would like to say "Hello, Arthur of the Round Table!".', {'name': [{'0': 'Arthur of the Round Table'}], '0': 'Arthur of the Round Table'})

Complicated Number Test - make sure it all works
In cases of invalid tests, it should match a lesser part of the number in most cases
42 (valid): 42
4d2 (invalid): 4
1701 (valid): 1701
1,701 (valid): 1,701
1,70,1 (invalid): 1
1,701.112 (valid): 1,701.112
1,701.112e10 (valid): 1,701.112e10
1,701.112e1,0 (invalid): 1,701.112e1

Speed Tests - lets see how fast it goes!
pattern make: (average of 200 tests)
0.004639228822180856
pattern match:
0.019925895326346654
```
Please note the speed test here is harder than the one given in the [read-me](README.md)
