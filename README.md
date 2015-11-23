---
output: html_document
---
# KG
Kurvengeräusche detektion

##algorithm
- squeal 1102 1976 Hz width < 10Hz
minimal duratuion 40-60 ms[](http://www.head-acoustics.de/downloads/de/NVH_User/Usergroupmeeting_2006/Blaschke_Peter/Comfort2006_Mauer.pdf)
 beginning abrupth
 -phase?

- flanging brodband
 beginning abrupt ending slow
 phase?


A. snkg =(livello totale -(flanging)livello filtrato lp 1500)
   smooth(snKg) (not simmetric (past!))
   kg if(snkg > delta)
   
B.

##Algorithm evaluation
specifity: true negative / false positive
sensityve: true positive / N positive events
##Kurvengerüsche package

## class
- measuredValues :
- time signals:
- dsp  : Calculate the squeal and flanging of a set of microphones given a set of signal during a passby
- vizualise Widget

### measuredValues

import hand handle mbbm measured and evaluated values in tables
store kg processed values
export data frames for further calculations

### time signals
handle the time signals of a given passby ID

## Squeal Noise 

Sqeal noise of a passby is a time function $z(t) \in \{ 0,1\}$. 0 is no squeal 1 is squeal. This function can be discretized in a time sequence $z_n = z(t_n)$ with $t_n = n \Delta t$. This is a given deterministic sequence.

We are interested in the quantity $T_z = \int z(t) dt = \sum z_n \Delta t$ of a given passby.

### Squel Noise detection

We have a detection algorithm (measurement of squeal noise) which has an output $M_n \in \{0,1\}$. The Algorithm is not perfect,  $M_n$ is random variable. The algorithm/ test of squel noise is characterized by:

- true positive rate (sensitivity): $P(M_n=1|z_n = 1) = p_{tp}(\{z_n\})$
- false positive rate: $P(M_n=1|z_n = 0) = 1 - p_{tn}(\{z_n\})$
- false segative rate: $P(M_n=0|z_n = 1) = 1 - p_{tp}(\{z_n\})$
- true negative rate(Specifity): $P(M_n=0|z_n = 0) = p_{tn}(\{z_n\})$

#### example of test
$M$ is a test to know if a person is allergic. $z$ is the allergic state of a person.
The tests has following charachteristics:

- true positive rate : $P(M=1|z = 1) = 0.8$
- false positive rate: $P(M=1|z = 0) = 0.1$
- false negative rate: $P(M=0|z = 1) = 0.2$
- true negative rate: $P(M=0|z = 0) = 0.9$

##### Question 1
`if a people has a positive  test  $M=1$ how is probable is that he is allergic?`
given that the true probability of allergic persons is $P(z=1)= pz = 0.01$ and $P(z=0)=1-pz = 0.99$

 - step 1: test probability outcome $P(M)$ on $z$:
  $P(M=1) = P(M=1|z = 1)\cdot P(z=1) + P(M=1|z = 0)\cdot P(z=0) = 0.8 \cdot 0.01 + 0.1\cdot 0.99$
  
  ```{r}
  pMz1 = c(0.8,0.1)
  pMz0 = c(0.2,0.9)
  pz = c(0.01,0.99)
  pM1 = sum(pMz1*pz)
  print(pM1)
  ```
  
  $P(M=0) = 0.2 \cdot 0.01 + 0.9\cdot 0.99$
  
  ```{r}
  pM0 = sum(pMz0*pz)
  print(pM0)
  ```
  
- step 2: The question anzwers is given by $$ P( z = 1 | M=1) = \frac{P( M = 1| z = 1 ) \cdot P(z=1)}{ P(M = 1)}$$
  
  ```{r}
  pz1M1 = 0.8*0.01/pM1 
  print(pz1M1)
  ```

#### question 2

`given a test and many outcomes, estimate $pz$`


#Selecting the intervals :
The script `run_CaseCreatorWidget.py` call the GUI to select intervals where one hears flanging or squealing noise.
Make sure there are the following files in the same path : 
- `caseToAnalyze.json` : Contains the mID to be analysed. Each entry looks like the following:
```{json}
"m_00403_4" : {
		"case" : {
			"location" : "Biel",
			"mID" : "m_00403",
			"measurement" : "Vormessung",
			"mic" : 4,
			"Te" : 19.0,
			"Tb" : -2.375,
			"author" : null
		},
		"wavPath" : "wav\\m_00403_mic_4.wav",
		"plotData" : {
			"LAfast" : [[-8.0, -7.875, ... , 53.8153076171875, 53.974822998046875]]
		},
		"tmax" : 21.203105926513672,
		"tmin" : -7.999987602233887
	}
```
- `AppCS` folder containing the `info.html` and `info.css` files for the information page. It also contains the icon, the images for the html page, and so on.
	
- `firstcases.json` (optional) : contains the first cases to evaluate from the `caseToAnalyze` list.

#Analysing the algorithms
To analyse how an algorithms selects the intervals and how it compares with authors selected cases, you can use `run_AdminAlgorithmWidgets.py` and select from Files/new Create new Admin.

#Building the exe file
We use cx_freeze package to build the executable file. Setup.py is the file to be called with cx_freeze using the following command (on Windows): 
`pathtopython\python cxsetup.py build`

This will create a folder called *build* aside the directory KG. You need to do the following in order to fix some cx_freeze issues (for points 1 and 2, the files are also available in the folder *missingFilesforExe*):
 1. Copy the file `_ufuncs.pyd` into build folder (you will find it under `pathtopython/lib/site-packages/scipy/special`
 2. Copy the files `libifcoremd.dll` and `libmmd.dll` into build folder (you will find them under `pathtopython/lib/site-packages/numpy/core`
 3. Move the folder `dateutils` from the zipped `build/library` into `build` (i.e. remove it from the archive and place it into build folder)
 4. Add the file `caseToAnalyse.json` in `build`
 5. Finaly add the corresponding wav files inside `build/wav`

# Creating an exportable package containing kg and mySTFT

First install distutils. To create the package run `python setup.py build`. Then to install the package use pip : `pip install kg`.
