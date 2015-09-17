##Kurvengeräsche package

## class
- measuredValues :
- time signals:
- dsp  : Calculate the squeal and flanging of a set of microphones given a set of signal during a passby
- vizualise Widget
- Interval: Create an interval. Needs two floats as bounds.

Attributes | type
--------   | -------
`xmin` | float
`xmax` | float

Method     | Description | Return type
----------- | ----------- | ------------
`get_x()` | gives xmin,xmax | two floats
`intersect(other)` | tests if intersection | boolean
`intersection(other)` | gives intesection | Interval
`difference(other)` | gives self minus other | Interval
`ispoint()` | tests if xmin==xmax | boolean
`contains(other)` | Tests if other is in self | boolean
`isin(other)` | tests if self is contained in other | boolean
`self < other` | `self.xmax < other.xmin` | boolean
`self > other` | `self.xmin > other.xmax` | boolean
`self==other` | same intervals | boolean
`self != other` | the two intervals are not intersecting | boolean
`self <= other` | not `self > other` | boolean
`self >= other` | not `self < other` | boolean
- SetOfIntervals: Create a list of intervals. No initialisation variables.

Attributes | type
---------- | ------
`RangeInter` | list of Intervals
`length` | integer
`sorted` | boolean

Method | Description | Return type
------ | ----------- | -----------
`R.append(a)` | add Interval `a` to `R` | none
`R.contains(a)` | test if `a` in `R` | boolean
`R.discretize(tb,te,dt)` | discretize `R` in `[tb,te]` step `dt` | list
`R.remove(a)` | remove Interval `a` from `R` | none
`R.removeIntersection(a)` | called by `remove()` | none
`R.haselement(a)` | test if `a` is an element of the list `R.RangeInter` | boolean
`R.sort()` | sorts Intervals in `R.RangeInter` | none

### measuredValues

import hand handle mbbm measured and evaluated values in tables
store kg processed values
export data frames for further calculations

### time signals
handle the time signals of a given passby ID

### DSP

### Copyrights

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licence Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />Ce(tte) œuvre est mise à disposition selon les termes de la <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Licence Creative Commons Attribution -  Partage dans les Mêmes Conditions 4.0 International</a>.