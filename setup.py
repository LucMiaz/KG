#---This setup will create a package containing kg and stft.
# This way, we can install kg on a computer. 
#
#To create the package:
#First install module distutils
#
#Then run "python distutils setup.py build"
#To install the package on a computer run the following:
#pip install kg
#!/usr/bin/env python
from distutils.core import setup

setup(name='kg',
      version='1.0',
      description='kg detection',
      author='esr',
      packages=['kg','mySTFT'],
     )
