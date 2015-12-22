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
```
