# PyPMEWS
A python implementation of the Pattern Matching and Extraction With Strings system.

#### TLDR;
Regex with a twist. Capture repeated groups if you want, and more consistent characters and meanings.

##### Important!
Implementation essentially completed, but 100% Python implementation means it mightn't be the fastest module you've seen (see below).

## How To Use
To create a pattern, just create a new `Matcher` object:

```python
#Create a new matcher with the expression, and store it away in `mypattern` for later use
mypattern = Matcher('he(l){2}o world(:\?)?') 
```

To use it, just match it against a string with the `match` method. You will receive a `Match` object.
```python
>>> match = mypattern.match('hello world?')   #See if 'hello world?' matches the expression
>>> match                                     #Access the match returned
"Match<he(l){2}o world(:\?)?>('hello world?', 'hello world?', {'0': '?'})"
>>> match == 'hello world?'                   #Compare if the entire match found is 'helloworld?'
True
>>> match.groups                              #All the capture groups collected
{'0': '?'}
```

Now you know this, you try and make much more complicated expressions, and have fun :grinning:! Use the [cheat sheet](#syntax) for guidance, and [`test.py`](test.py) contains some examples.

#### Does it work?
To make sure everything works, please run `test.py`, which should output something like [this](testresults.md).

#### Speed
* To create the `Matcher` object in the example above, which is when the matching tree is built, in a test took around 3ms
* The match itself, took around 10 ms
* Using the search method, can take significantly longer, but in general doesn't

Speed in matching is currently the main problem, probably due to the recursive approach. A iterative approach may be taken to speed things up in the future.

## Syntax
* `\<char>` - escape character
  * `\d` - number [0-9]
  * `\c` - letter [A-Za-z]
  * `\s` - space/tab [  ]
  * `\w` - alphanumerical [A-Za-z0-9]
  * `\n` - newline
  * `\b` - breaker [\n\s] 
* `.` - universal character (except `\n`)
* `{num}` - number repeats
  * `{x-y}` - from x to y repeats
  * `{-y}` - as many as y repeats
  * `{x-}` - at least x repeats
  * `*` - 0 or more repetitions
  * `+` - 1 or more repetitions
  * `?` - 0 or 1 repetition (optional)
  * `[*+?]%` - greedless, try as few as possible
  * `{%x-y}` - greedless range of repeats
* `[xyz]` - any of x, y or z
  * `[^xyz]` - anything but x, y, or z
* `(expr)` - a subexpression
  * `(:expr)` - a capture group
  * `([]:expr)` - a capturing collection, will not overide, but instead generate a list, such as when you need to accumulate captures of repeated segments
  * `(name:expr)` - a named capture group
  * `(name[]:expr)` - a named capturing collection
  * `(name$:expr)` - a named capturing group with an autofilled number (`$` works anywhere)
* `(expr_x|expr_y)` - choice
* `<x>` - a link, to an expression named x
  * `<name:x>` - a captured link to x

No `^` start and `$` end yet. Just use methods to achieve same effect.

## Release Changes

### What's new in 1.0.1 - Aldwych

#### Features
* Added compatibility with Python 3.4, and probably as low as 3.2

### What's New in 1.0.0 - Aldwych

#### Features
* `test.py` new testing suite to make sure installation completed properly, and as an example, including a new speed test, and more complicated tests

#### Fixes
* Issue #7 has been fixed, meaning:
  * Extra matching has been resolved by realising the first checks should be checking this node and not branches for emptiness, which actually greatly simplifies it.
  * Also, though if the first emptiness checks find a join with an empty join, they will treat that also as a match, which makes it complicated again.
  * Laziness :last_quarter_moon_with_face:, which has been at the end of groups, has been solved by changing `match` -> `Match()`, because, although `match` might have seemed empty, the tree matching section actually filled it. This does not go against a previous problem where correctly matched trees we're failing, this was done in between where adding to it instead of creating anew occurred.
* Timings now done with python module
* Code clean up, deployment ready clean up, random tests and debugs everywhere swept away
* `README.md` more complete

### What's New in 0.2.1
#### Features
* Links now collect in sub-dictionaries, which allows for better processing of them, and lists of them to happen
```python
>>> mypattern = Matcher('Hello, (:<name[]:name>)!', 
                         links={'name': Parser(r'(:[A-Z]\c+ (\c{2-} )*[A-Z]\c+)')})
>>> match = mypattern.search('I would like to say "Hello, Arthur of the Round Table!".')
#Displayed here over multiple lines for easier viewing
'''Match<Hello, (:<name[]:name>)!>(\'Hello, Arthur of the Round Table!\',
\'I would like to say "Hello, Arthur of the Round Table!".\',
{\'name\': [{\'0\': \'Arthur of the Round Table\'}], \'0\': \'Arthur of the Round Table\'})''' 
```
* The new `$` symbol, for use in names is automatically replaced with the current count (increasing it). This allows for names which automatically have numbers in them, to differentiate them
```python
'(hello$:...)...' -> {'hello0': ...}
```

#### Bug Fixes
* `+` and `*` now work with trees at the end of a group
* Code cleaned up a little, removed some comments on debugging *etc.*

### What's New in 0.2.0
#### Features
* New Links, references to other expressions stored in the matcher, introduced to allow subexpressions to be added, and increase clarity. They are worked out on matching to avoid endless strings in case of recursion
```python
>>> mypattern = Matcher('Hello, <name:name>!', links={'name': Parser(r'[A-Z]\c+ (\c{2-} )*[A-Z]\c+')})
>>> match = mypattern.search('I would like to say "Hello, Arthur of the Round Table!".')
>>> match
"Match<Hello, <name:name>!>('Hello, Arthur of the Round Table!', 'I would like to say \"Hello, Arthur of the Round Table!\".', {'name': 'Arthur of the Round Table'})"
```
#### Bug Fixes
* Opened a trove:
  * `+` now gives up
  * ranges working again (checking on a generator expression depleted it, changed to list comprehension)
