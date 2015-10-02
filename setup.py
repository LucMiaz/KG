#!/usr/bin/env python
# http://venkateshwaranloganathan.com/2013/11/01/distribute-your-python-programs-at-ease/
from cx_Freeze import setup, Executable
import sys
if sys.platform == "win32":
    base = "Win32GUI"
build_exe_options = {
                    "icon":'icon.ico',
                    "compressed":True,
                    "zip_includes":['kg','mySTFT'],
                    'packages':['scipy'],
                    'build_exe':'../build/',
                    }

setup(name = "KG Detection",
      version = "0.9",
      description = "Graphical Interface of noise range selection : Please select the intervals where you here either Kreischen or Zischen.",
      executables = [Executable("Measurements_example/MBBMZugExample/test_cases/run_CaseCreatorWidget.py")],
      options = {"build_exe": build_exe_options},)