##Kurvengeräsche package

## Classes
### measuredValues :
### time signals:
### dsp  : Calculate the squeal and flanging of a set of microphones given a set of signal during a passby 
### vizualise Widget
### Interval: 
    **Create an interval**. Needs two floats as bounds.

Attribute | type
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

###SetOfIntervals: 
**Create a list of intervals**. No initialisation variables.

Attribute | type
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

### Case :
    **Define a case of study**.
    
Attribute | description | type | needed at init
--------- | ----------- | --------- | ----------------
`measurement` | | float | [x]
`mID` | | string | [x]
`mic` | | integer | [x]
`author` | | string | [x]
`date` | | string | []
`tb` | begin time | float | [x]
`te`| end time | float | [x]
`Z` |  | SetOfIntervals | []
`K` | screeching sound | SetOfIntervals  | []

Method | Description | Return type
------ | ----------- | -----------
`add_kg_event(self, t0, t1, [noiseType])` | create an interval [t0,t1], update LastInterval and add this interval to noiseType | none
`remove_last_event(self, [noiseType]) | Remove the last interval selected from the set of interval | none
`save(self, mesPath)` | save Case to file | none
`_compare(self, detect , [noiseType], bool[sum]) | compare detection algorithm results with Case, True/False Positive/Negative | list, list, list, list 
`test(self, algorithm, mesVar, [signal], [sum])` | test algorithm  on Case | list

### measuredValues

import hand handle mbbm measured and evaluated values in tables
store kg processed values
export data frames for further calculations

### time signals
handle the time signals of a given passby ID

### DSP

## Copyrights

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licence Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />Ce(tte) œuvre est mise à disposition selon les termes de la <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Licence Creative Commons Attribution -  Partage dans les Mêmes Conditions 4.0 International</a>.