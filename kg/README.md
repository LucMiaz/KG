#Kurvengeräsche package
**Table of Contents**
- [Classes](#classes)
	- [Interval](#interval)
	- [SetOfIntervals](#setofintervals)
	- ~~[GraphicalInterval](#graphicalinterval)~~
	- [DetectControlWidget](#detectcontrolwidget)
	- [CaseCreatorWidget](#casecreatorwidget)
	- [Case](#case)
	- [MicSignal](#micsignal)
	- [time signals](#time-signals)
- [Copyrights](#copyrights)

***

## Classes
### time signals:

### dsp 
**Calculate the squeal and flanging** of a set of microphones given a set of signal during a passby 

### Interval
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

### SetOfIntervals
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

### ~~GraphicalInterval~~ (removed and replaced by `DetectControlWidget`)

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

### DetectControlWidget

**DetectControlWidget is an abstact class whose main purpose is to initialize the media controls (i.e. handling the audio input and graphical interface).**

Attributes | type
---------- | --------
`adminsession` | boolean
`tShift` | float
`t` | float
`mpl` | dict
`ca_update_handle` | list
`ca_set_bar_handle` | list
`barplay` | boolean
`savefolder` | pathlib Path
`media` | Phonon.MediaObject
`audio_output` | Phonon.AudioOutput
`seeker` | Phonon.SeekSlider
`mediarate` | String
`comboratedict` | dict
`comboratelist` | list
`vBox` | QtGui.QVBoxLayout


Methods:
name | takes | returns | description
----- | ----- | ----- | ------
`_barplay` | boolean | None | defines what to do when audio is playing/not playing
`case_down` | - | None | abstact class
`case_up` | - | None | abstact class
`chg_folder` | - | None | abstract class
`change_plot`| - | None | abstract class
`change_quality`| - | None | abstract class
`chg_type`| - | None | abstract class
`chg_typedisplay`| - | None | abstract class
`connections` | - | None | Sets the connections for media.tick, media.finished. media.stateChanged and calls _connections()
`_connections` | - | None | abstract class
`define_actions` | - | None | Defines the actions exitAction, showinfoAction, saveAction, changesavingfolderAction, playPauseAction, stopAction, nextcaseAction and prevcaseAction.
`keyPressEvent` | event | None | Defines actions for Keyboard shortcuts (see info.html for description)
`keyReleaseEvent` | event | None | see `keyPressEvent`.
`media_finish` | - | None | Defines what to do when media.finished is connected
`menu_ bar` | - | None | Sets the menubar with the action previously defined with `define_actions`.
`playPause` | - | None | Plays or pause the audio (depending on current state)
`set_int`| - | None | abstract class
`set_quality`| - | None | abstract class
`set_remove`| - | None | abstract class
`save_case`| - | None | abstract class
`setCentraWidget` | - | None | abstract class
`set_centralWidget`| - | None | add vBox to the displays (calls `setCentralWidget`)
`set_ media_ source`| pathlib Path, *float*, *options* | None | Sets the audio source to the file in the given path.
`set_mpl`| *dict* | None | adds canvas
`show_info`| - | None | abstract class
`timer_status` | bool, bool | None | changes the timer status according to played audio
`update_time` | float | None | updates t with tShift and float given divided by 1000. Calls update _canvas
`update_canvas`| - | None | calls `set _ bar _ position` and `ca _ update _ handle`.
`alg_results` | micSignal, algorithm | None | classmethod (cls, micSn, algorithm) 

### CaseCreatorWidget
**subclass of DetectControlWidget**
This widget should allow to create cases in GUI style kg_ event duration is selected with mouse cursor case is saved using a button case_dicts contains the following attributes:
name | type |
---- | ---- |----
`mainPath` | str |
`Paths` | list of pathlib paths | contains pathlib Paths to the raw data (actually to the folder containing the dir `raw_signals`)
`infofolder` | pathlib path | path to the folder with the info.html
`minspan` | float|
`PlotTypes` | list|
`currentplottype` | String |
`author` | string |
`sparecase`|tuple|
`AuthorCases` | dict|
`casesToAnalyze` | dict|
`both_visibles` | bool | if K and Z intervals are displayed or not
`NoiseTypes` | list of strings |
`ccaseDict` | dict | With the following attributes
||case: Case() instance
||plot: {pName:[t,y],...}
||tmin: flt
||tmax: flt
||wavPath: str

Methods:
Name | input | output | description
--- | ----- | ----- |-----
`add_new_cases` | - | -|asks for adding a new case
`add_int`|float, float | - | adds an interval
`add_widgets_admin` | - | - | adds admin tools such as different types of plot, algorithm test and authors browser
`add_widgets_basic` | - |- | creates the default interface
`add_widget_extended` | - | -| add widgets that are not useful when logged as admin
`admin_actions` | - | - | creates admin actions
`asks_for_algorithm`|-|-|queries the desired algorithms
`asks_for_author`|-|-| queries who's there
`asks_for_case` | -|-|asks for new case add
`_barplay` | bool | - |tells what to do if audio is playing or not
`case_down` | - |-|changes case to the next one
`case_to_analyse` | string, int, path, *string*|-|setup the analysed cases from MBBM. Needs ID, mic, matPath, givenauthor=None. Is called by load_cases
`case_up` |- |-|changes case to the previous one
`change_current_case` | int |- | changes current case to the i-th item in CaseCombo
`change_quality` | string | - | sets the quality depending on input (which must be in  ['good','medium','bad']
`changeplot` | - | - | changes the plottype
`chg_folder` | -|-| change the directory where to save the data
`check_rb` | string | -  | sets the qradios buttons
`checkSavedCases`| - | list | gets the cases saved by current author in savefolder/test_cases/author
`chg_type` |-|-|change the noise type to the next one on the list (and back to the first)
`chg_typedisplay`|-|-|toggle between show both and show one
`_connections`|-|-|connects the buttons/combobox to the methods to be applied
`extbrowsercall`|-|-|call opening info page in external web browser
`get_quality` |-|-| returns current quality
`hide_rect`|-|-|hides the rectangles without touching the SOI
`import_cases`|-|-|performs the basic import of cases"
`load_algorithm` | int |-|loads the algorithm selected
`load_author` | int |-|loads the saved intervals of an author
`load_cases` | list | -| loads the cases given in list of paths to casesToAnalyse. Is called by `add_case` and by `asks_for_ncases`.
`onclick` | interval | - | removes interval
`onselect` | float, float, *bool* |-| adds interval1
`plot` |-|-|
`plotchange` | int | - | changes the plot to index
`remove_int` | float, *float* | - | removes an interval
`save_case` |-|-| saves the case
`set_both_visible` | bool |-| toogle Z/K intervals visibility
`set_current_case` | string | - | sets the current case
`set_int` | bool | - | adds a float as first bound to a currently spanned interval (useful when selecting while audio is played)
`set_noise_type` | int | - | changes noise type
`set_remove` | bool | - | removes int while playing audio (nemesis of `set _int`)
`show_compare` | bool | -| will show or remove the comparison between current author /current case and the current algorithm
`show_info` |-|-|
`TurnTheSavedGreen`|-|-| as its name tells, it turns the saved cases green. It initiates the combobox Casecombo and it also load the intervals saved
`unsave`|-|-|get back to unsaved status
`update_stay_rect` | *bool*|-| updates the intervals that must be shown
`from_measurement`|many|-| classmethod : (cls, mesVal, mID, mics, author = None)

Other method : 
`load_micSn(ID,mic,matPath, algorithm=None,gvar = ['Tb','Te','Tp_b','Tp_e','LAEQ'] )` |loads micSn from the matPath, returns a signal and a stftName

### Case
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

### MicSignal

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
`from_measurement(cls, mesValues, ID, mic)` | classmethod : constructs directly a MicSignal object | None


function | description | return
-------- | -------- | --------
`isclipped(xn, K=301, threshold=0.55, axdisplay=None, normalizehist=False)` | Tells if the signal xn is clipped or not based on the test by Sergei Aleinik, Yuri Matveev (see ref in detect.py) | boolean
`histogram(xn, K, display=None, normalize=False)` | returns the function histogram of discrete time signal xn with K bins in histogram | list (opt. plot)

### time signals
handle the time signals of a given passby ID

***

## Copyrights

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Licence Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />Ce(tte) œuvre est mise à disposition selon les termes de la <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Licence Creative Commons Attribution -  Partage dans les Mêmes Conditions 4.0 International</a>.
