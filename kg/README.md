##Kurvengeräsche package

## Classes
### measuredValues :
### time signals:

### dsp  : 
**Calculate the squeal and flanging** of a set of microphones given a set of signal during a passby 

### vizualise Widget

### Interval:
**Creates an interval**. Needs two floats as bounds.

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
`contains(other)` | tests if other is in self | boolean
`isin(other)` | tests if self is contained in other | boolean
`self < other` | `self.xmax < other.xmin` | boolean
`self > other` | `self.xmin > other.xmax` | boolean
`self==other` | same intervals | boolean
`self != other` | the two intervals are not intersecting | boolean
`self <= other` | not `self > other` | boolean
`self >= other` | not `self < other` | boolean
`toJSON(rounding)`     | JSON format of Interval, wt rounding   | dict

### SetOfIntervals: 
**Creates a list of intervals**. No initialisation variables.

Attribute | type
---------- | ------
`RangeInter` | list of Intervals
`length` | integer
`sorted` | boolean

Method | Description | Return type
------ | ----------- | -----------
`R.append(a)` | adds Interval `a` to `R` | none
`R.contains(a)` | tests if `a` in `R` | boolean
`R.discretize(timeparam)` | discretizes `R` in `[tb,te]` step `dt`. Gives $\Xi_{\text{RangeInter}}(\text{Range(tb,te,dt)})$ Use ordering=False to avoid ordering (for example, with ordering, if you want to discretize on (0.1,10.1) with delta (1.), it will be changed to (1.,10.1) delta (0.1) | list
`R.remove(a)` | removes Interval `a` from `R` | none
`R.removeIntersection(a)` | called by `remove()` | none
`R.haselement(a)` | tests if `a` is an element of the list `R.RangeInter` | boolean
`R.sort()` | sorts Intervals in `R.RangeInter` | none
`isempty()` | tells if self is empty
`toJSON(rouding=0)` | JSON serializable representation of self, with optional rounding (0 = no rounding)
`fromJSONfile(filename)` | adds Intervals to self from a JSON file directly
`fromJSON(data)` | adds Intervals to self from data (in JSON format). Takes the list of interval from 'SetOfIntervals' index
`save(self, filename)` | saves self to filename in json

### GraphicalInterval

 **Graphical support for SetOfIntervals.** 
 
 Have a list called `Rectangles` corresponding to intervals of the class `SetOfIntervals`. This list containts duples : an Interval and a patch (displayed rectangle) linked to an axis (stored in self.ax). This allows to update `Rectangle` from the SetOfInterval attribute `RangeInter` and vice versa, i.e. when we want to delete a displayed patch, we look it up in `Rectangle` (by itering over its second argument), and then we can delete the corresponding `Interval` in `RangeInter`.\n

Method | Description
------- | ----------
`_update()` | updates Rectangles and plot them
`on_select(eclick, erelease)` | adds the interval selectionned while holding left mouse click
`connect(rect)` | connects the rectangle rect to the figure
`removerectangle(rect)` | removes rect from the figure, from Rectangles list and removes the corresponding interval from RangesInter
`on_pick(event)` | removes the interval selectionned while holding right mouse click
`toggle_selector(event)` | handles key_events
`call_discretize(event)` | calls the method `discretize` from an event, such as a button
`changeDiscretizeParameters(listofparams)` | changes the parameters of the discretization (usefull if calling with button). Please give a list or a tuple of length 3
`discretize(zerotime, endtime, deltatime, axis=self.axis)` | returns the characteristic function of range(zerotime,endtime, deltatime) in respect to RangeInter. Optional argument is the axis where one need to represent the points of the characteristic function. If one does not want any graphical representation, give None as axis


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
`Z` | Flanging noise | SetOfIntervals | []
`K` | Squeal noise | SetOfIntervals  | []

Method | Description | Return type
------ | ----------- | -----------
`add_kg_event(t0, t1, [noiseType])` | create an interval [t0,t1], update LastInterval and add this interval to noiseType | none
`remove_last_event([noiseType]) | Remove the last interval selected from the set of interval | none
`save(self, mesPath)` | save Case to file | none
`_compare(detect , [noiseType], bool[sum]) | compare detection algorithm results with Case, True/False Positive/Negative | list, list, list, list 
`test(algorithm, mesVar, [signal], [sum])` | test algorithm  on Case | list
`toJSON(filename=None)` | returns the essential informations of self, if Pathname or Path is given, save in file.

### measuredValues

import hand handle mbbm measured and evaluated values in tables
store kg processed values
export data frames for further calculations

Audio file and the relation for amplitude pressure DV
    
data attributes:
- WavData: dict of np arrays containing the time signal
- Calc: dict of calulated quantity
- KG: results quantity about Kurvengeräusche  

methods | description | return
-------- | --------- | -------
`clippedtest(K=301, threshold=0.55, ax=None, normalize=False, overwrite=False, fulllength=False)` | Calls function `isclipped` on mask tb-te (only if fulllength=False). Saves the result in `self.micValues`. Only process if there isn't already a item `isclipped` in micValues. To overrule this, pass overwrite=True in method call. If an ax is given, the plot of the histogram will be display. if normalize is True, the histogram will be normalizes | boolean   
`calc_stft(self, M , N = None, overlap = 2, window = 'hann',**kwargs)` | calculates the stft |
`calc_PSD_i(stftName, **kwargs)` | calculates PSD for all frames f_i | None
`calc_kg(algorithm)` | runs algorithm on MicSignal object. parameter : algorithm instance | None
`get_stft_name(algorithm)` | gets name of stft | string
`get_KG_results(algorithm)` | gets values in self.KG for algorithm | {'ID':mID, 'mic': mic, 'results':{...}}
`get_mask(t = None , tlim = None)` | calculate mask for time vector according tlim. default with MBBM evaluation | list of booleans
`plot_spectrogram(name, ax, freqscale = 'lin', dBMax = 110)` | plot spectrogram | plot
`plot_triggers(self, ax, type ='eval', **kwargs)` | type: eval for MBBM evaluations bounds. type passby passby times | plot  
`plot_KG(algorithm, ax, **kwargs)` | plot detection results for a given algorithm | plot       
`plot_BPR(algorithm, ax, label = None,**kwarks)` |  plot detection results for a given algorithm | plot
`plot_signal(ax , label = None,**kwargs)` | plot signal | plot
`export_to_Wav(wawPath = None)` | Export a .wav file of the signal in mesPath\wav with mesPath: main measurement path | libpath Obj: path of wavfile
`from_measurement(cls, mesValues, ID, mic)` | classmethod : constructs directly a measuredValues object | None


function | description | return
-------- | -------- | --------
`isclipped(xn, K=301, threshold=0.55, axdisplay=None, normalizehist=False)` |
    Tells if the signal xn is clipped or not based on the test by Sergei Aleinik, Yuri Matveev (see ref in detect.py) | boolean
`histogram(xn, K, display=None, normalize=False)` | returns the function histogram of discrete time signal xn with K bins in histogram | list (opt. plot)

### time signals
handle the time signals of a given passby ID

### DSP

***

## Copyrights

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licence Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />Ce(tte) œuvre est mise à disposition selon les termes de la <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Licence Creative Commons Attribution -  Partage dans les Mêmes Conditions 4.0 International</a>.