#!/usr/bin/env python
#run "python cxsetup.py build"
# http://venkateshwaranloganathan.com/2013/11/01/distribute-your-python-programs-at-ease/
from cx_Freeze import setup, Executable
import sys
if sys.platform == "win32":
    base = "Win32GUI"
build_exe_options = {
                    "icon":'AppCS/icons/icon3.ico',
                    "compressed":True,
                    "zip_includes":['kg','mySTFT'],
                    'packages':['scipy'],
                    'build_exe':'../build/',
                    }

setup(name = "KG Detection",
      version = "1.0",
      description = "Graphical Interface of noise range selection : Please select the intervals where you here either Kreischen or Zischen.",
      executables = [Executable("run_CaseCreatorWidget.py")],
      options = {"build_exe": build_exe_options},)