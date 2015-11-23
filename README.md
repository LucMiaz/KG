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
			"LAfast" : [[-8.0, -7.875, -7.75, -7.625, -7.5, -7.375, -7.25, -7.125, -7.0, -6.875, -6.75, -6.625, -6.5, -6.375, -6.25, -6.125, -6.0, -5.875, -5.75, -5.625, -5.5, -5.375, -5.25, -5.125, -5.0, -4.875, -4.75, -4.625, -4.5, -4.375, -4.25, -4.125, -4.0, -3.875, -3.75, -3.625, -3.5, -3.375, -3.25, -3.125, -3.0, -2.875, -2.75, -2.625, -2.5, -2.375, -2.25, -2.125, -2.0, -1.875, -1.75, -1.625, -1.5, -1.375, -1.25, -1.125, -1.0, -0.875, -0.75, -0.625, -0.5, -0.375, -0.25, -0.125, 8.881784197001252e-15, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25, 1.375, 1.5, 1.625, 1.75, 1.875, 2.0, 2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875, 3.0, 3.125, 3.25, 3.375, 3.5, 3.625, 3.75, 3.875, 4.0, 4.125, 4.25, 4.375, 4.5, 4.625, 4.75, 4.875, 5.0, 5.125, 5.25, 5.375, 5.5, 5.625, 5.75, 5.875, 6.0, 6.125, 6.25, 6.375, 6.5, 6.625, 6.75, 6.875, 7.0, 7.125, 7.25, 7.375, 7.5, 7.625, 7.75, 7.875, 8.0, 8.125, 8.25, 8.375, 8.5, 8.625, 8.75, 8.875, 9.0, 9.125, 9.25, 9.375, 9.5, 9.625, 9.75, 9.875, 10.0, 10.125, 10.25, 10.375, 10.5, 10.625, 10.75, 10.875, 11.0, 11.125, 11.25, 11.375, 11.5, 11.625, 11.75, 11.875, 12.0, 12.125, 12.25, 12.375, 12.5, 12.625, 12.75, 12.875, 13.0, 13.125, 13.25, 13.375, 13.5, 13.625, 13.75, 13.875, 14.0, 14.125, 14.25, 14.375, 14.5, 14.625, 14.75, 14.875, 15.0, 15.125, 15.25, 15.375, 15.5, 15.625, 15.75, 15.875, 16.0, 16.125, 16.25, 16.375, 16.5, 16.625, 16.75, 16.875, 17.0, 17.125, 17.25, 17.375, 17.5, 17.625, 17.75, 17.875, 18.0, 18.125, 18.25, 18.375, 18.5, 18.625, 18.75, 18.875, 19.0, 19.125, 19.25, 19.375, 19.5, 19.625, 19.75, 19.875, 20.0, 20.125, 20.25, 20.375, 20.5, 20.625, 20.75, 20.875, 21.0, 21.125], [39.44554138183594, 45.170291900634766, 46.15115737915039, 46.55803298950195, 47.278743743896484, 47.214698791503906, 46.95414733886719, 47.24322509765625, 47.381492614746094, 47.416900634765625, 46.78630828857422, 46.58533477783203, 47.441795349121094, 47.42448806762695, 47.67581558227539, 48.782508850097656, 49.36613082885742, 49.50060272216797, 49.35336685180664, 49.418365478515625, 49.150001525878906, 49.1661376953125, 50.40758514404297, 51.88520050048828, 52.98876190185547, 54.438785552978516, 54.14901351928711, 54.55792236328125, 55.01801300048828, 55.37948989868164, 55.90584182739258, 56.79985809326172, 56.858238220214844, 57.199310302734375, 57.9713249206543, 59.14910125732422, 60.08519744873047, 60.71783447265625, 60.819000244140625, 62.55760192871094, 62.0283317565918, 61.44933319091797, 61.47007369995117, 59.85824966430664, 59.67164611816406, 61.36627197265625, 64.43060302734375, 65.54449462890625, 65.96161651611328, 67.60655212402344, 70.30525970458984, 72.52790069580078, 71.68511199951172, 70.34381866455078, 69.79591369628906, 71.88098907470703, 73.1496353149414, 72.52101135253906, 72.02345275878906, 70.89390563964844, 70.78500366210938, 72.16864013671875, 73.82322692871094, 73.41992950439453, 71.24665069580078, 70.60542297363281, 71.09492492675781, 71.049072265625, 70.5042724609375, 71.27679443359375, 72.5353012084961, 74.38507843017578, 74.15361022949219, 72.66939544677734, 70.969482421875, 70.03056335449219, 70.26557159423828, 70.13278198242188, 71.72520446777344, 71.85136413574219, 71.01272583007812, 70.80391693115234, 72.90811920166016, 74.13224029541016, 75.9212875366211, 74.87406921386719, 76.27076721191406, 78.29360961914062, 79.17617797851562, 78.03929901123047, 76.82762908935547, 77.8565673828125, 79.43451690673828, 82.07938385009766, 82.27923583984375, 84.33025360107422, 85.92948913574219, 85.59498596191406, 84.44624328613281, 86.22161102294922, 84.81405639648438, 85.09196472167969, 84.36019134521484, 83.39409637451172, 83.09005737304688, 83.91311645507812, 84.21611785888672, 84.37803649902344, 84.85601806640625, 83.95561981201172, 81.38152313232422, 79.71977996826172, 78.17190551757812, 77.48606872558594, 75.86600494384766, 74.82048797607422, 75.07581329345703, 74.37651062011719, 73.23487091064453, 73.1163558959961, 72.67665100097656, 72.66841125488281, 72.46315002441406, 72.48434448242188, 72.11134338378906, 72.45671081542969, 73.98313903808594, 74.20197296142578, 74.18941497802734, 74.22091674804688, 74.7297592163086, 75.56285858154297, 76.05680847167969, 76.26627349853516, 76.6319580078125, 77.80572509765625, 78.7838134765625, 79.17146301269531, 79.71119689941406, 79.66236114501953, 81.32945251464844, 82.04544830322266, 82.58143615722656, 84.39053344726562, 82.23323822021484, 82.20561218261719, 82.64713287353516, 81.96636962890625, 81.26914978027344, 80.61051177978516, 81.43376159667969, 82.64483642578125, 82.26791381835938, 79.93366241455078, 78.74556732177734, 77.70494079589844, 77.23164367675781, 77.95793914794922, 78.0775375366211, 77.62467956542969, 77.74176025390625, 77.88935089111328, 77.96347045898438, 77.5234146118164, 78.4234848022461, 78.83450317382812, 79.65790557861328, 80.19082641601562, 82.09812927246094, 80.97450256347656, 82.14303588867188, 84.17405700683594, 83.91967010498047, 84.00242614746094, 82.01580810546875, 81.05628204345703, 79.37677764892578, 77.60066223144531, 75.44012451171875, 74.32160186767578, 73.97169494628906, 73.27721405029297, 72.59268188476562, 70.94305419921875, 69.97582244873047, 71.1797866821289, 71.43289184570312, 70.65568542480469, 70.1893310546875, 69.78853607177734, 68.6885986328125, 68.22917175292969, 66.60344696044922, 66.07292938232422, 66.13654327392578, 66.93009185791016, 65.89379119873047, 65.51124572753906, 65.68118286132812, 64.99729919433594, 65.07548522949219, 66.16543579101562, 65.18841552734375, 63.9996337890625, 63.45929718017578, 63.024208068847656, 62.34727478027344, 61.646881103515625, 61.33621597290039, 62.23375701904297, 63.6323356628418, 62.09040832519531, 62.44732666015625, 63.1522331237793, 61.921470642089844, 61.05195999145508, 60.5970344543457, 60.30876541137695, 59.24231719970703, 58.41483688354492, 60.35110855102539, 61.851654052734375, 60.239097595214844, 59.365447998046875, 58.72608184814453, 57.87111282348633, 57.56360626220703, 58.869834899902344, 58.737396240234375, 56.84395217895508, 55.423133850097656, 54.63969802856445, 53.8153076171875, 53.974822998046875]]
		},
		"tmax" : 21.203105926513672,
		"tmin" : -7.999987602233887
	},

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