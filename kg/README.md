##Kurvengeräsche package

## class
- measuredValues :
- time signals:
- dsp  : Calculate the squeal and flanging of a set of microphones given a set of signal during a passby
- vizualise Widget
- Interval: Create an interval. Needs two floats as bounds. Methods : `get_x()` returns xmin,xmax; `intersect(other)`, `intersection(other)`, `difference(other)` which returns self minus other; `ispoint()` returns True if xmin==xmax; `contains(other)` returns True if other is in self; `isin(other)` returns True if self is contained in other; `self < other` if `self.xmax < other.xmin`; `self > other` if `self.xmin > other.xmax`; `self==other` means the two intervals are the same; `self != other` if the two intervals are not intersecting; `self <= other` if the interval `self` is not greater than `other`; similarly for `self >= other`.
- SetOfIntervals: Create a list of intervals. Intervals must be added with `R.append(a)`. To test if float `a` is in RangeOfIntervals `R` use `R.contains(a)`. To discretize `R` use `R.discretize(zerotime, endtime, deltatime)` where `zerotime` is the lower bound of the discretization, `endtime` is the greater bound and `deltatime` is the step. Other methods include : `remove()`, `removeIntersection()`, `haselement()` and `sort()`.

### measuredValues

import hand handle mbbm measured and evaluated values in tables
store kg processed values
export data frames for further calculations

### time signals
handle the time signals of a given passby ID

### DSP

### Copyrights

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licence Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />Ce(tte) œuvre est mise à disposition selon les termes de la <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Licence Creative Commons Attribution -  Partage dans les Mêmes Conditions 4.0 International</a>.