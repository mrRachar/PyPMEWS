# PyPMEWS
A python implementation of the Pattern Matching and Extraction With Strings system.

#### TLDR;
Regex, but different: captures all repeated groups (if you want it to), slightly more consistant symbols

##### Important!
Implementation practically completed, all features implemented. Does not have `^` start and `$` end yet, and also not ready for production use, as there may be a bug or two (or more).
100% Python implementation means it mightn't be the fastest module you've seen

##How To Use
To create a pattern, just create a new `Matcher` object:

```mypattern = Matcher('he(l){2}o world(:\?)?')```

To use it, just match it against a string with the `match` method. You will recieve a `Match` object.

```
>>> match = mypattern.match('hello world?')
>>> match
Match<he(l){2}o world(:\?)?>('hello world?', 'hello world?', {0: '?'})
```

##Syntax
* `\<char>` - escape character
  * `\d` - number
  * `\c` - letter
  * `\s` - space/tab
  * `\w` - alphanumerical
  * `\n` - newline
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
  * `(<name>:<expr>)` - a named capture group
* `(<expr_x>|<expr_y)` - choice

