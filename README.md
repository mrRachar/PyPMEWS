# PyPMEWS
A python implementation of the Pattern Matching and Extraction With Strings system.

#### TLDR;
Regex, but different: captures all repeated groups (if you want it to), slightly more consistant symbols

##### Important!
Implementation practically completed, all features implemented. Does not have `^` start and `$` end yet, and also not ready for production use, as there may be a bug or two (or more).
100% Python implementation means it mightn't be the fastest module you've seen

##How To Use
To create a pattern, just create a new `Matcher` object:

```python
#Create a new matcher with the expression, and store it away in `mypattern` for later use
mypattern = Matcher('he(l){2}o world(:\?)?') 
```

To use it, just match it against a string with the `match` method. You will recieve a `Match` object.
```python
>>> match = mypattern.match('hello world?')   #See if 'hello world?' matches the expression
>>> match                                     #Access the match returned
"Match<he(l){2}o world(:\?)?>('hello world?', 'hello world?', {'0': '?'})"
>>> match == 'hello world?'                   #Compare if the entire match found is 'helloworld?'
True
>>> match.groups                              #All the capture groups collected
{'0': '?'}
```

####Speed
* To create the `Matcher` object in the example above, which is when the matching tree is built, in a test took around 3ms
* The match itself, took around 10 ms
* Using the search method, can take significantly longer, but in general doesn't

Speed in matching is currently the main problem, probably due to the recursive approach. A iterative approach may be taken to speed things up in the future.

##Syntax
* `\<char>` - escape character
  * `\d` - number [0-9]
  * `\c` - letter [A-Za-z]
  * `\s` - space/tab [  ]
  * `\w` - alphanumerical [A-Za-z0-9]
  * `\n` - newline
  * `\b` - breaker [\n\s] 
* `.` - universal character (except `\n`)
* `{<num>}` - number repeats
  * `{<x>-<y>}` - from x to y repeats
  * `{-<y>}` - as many as y repeats
  * `{<x>-}` - at least x repeats
  * `*` - 0 or more repetitions
  * `+` - 1 or more repetitions
  * `?` - 0 or 1 repetition (optional)
  * `[*+?]%` - greedless, try as few as possible
  * `{%<x>-<y>}` - greedless range of repeats
* `[<x><y><z>]` - any of x, y or z
  * `[^<x><y><z>]` - anything but x, y, or z
* `(<expr>)` - a subexpression
  * `(:<expr>)` - a capture group
  * `([]:<expr>)` - a capturing collection, will not overide, but instead generate a list, such as when you need to accumulate captures of repeated segments
  * `(<name>:<expr>)` - a named capture group
  * `(<name>[]:<expr>)` - a named capturing collection
* `(<expr_x>|<expr_y)` - choice

