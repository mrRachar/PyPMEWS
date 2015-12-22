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
* `(expr_x|expr_y)` - choice
* `<x>` - a link, to an expression named x
  * `<name:x>` - a captured link to x

No `^` start and `$` end yet. Just use methods to achieve same effect.

## Release Changes
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
