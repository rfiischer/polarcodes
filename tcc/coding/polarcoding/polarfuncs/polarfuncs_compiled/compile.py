"""
Compile the Pythran optimization

Created on 09/03/2020 14:19

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

import pythran

pythran.compile_pythranfile("../polarfuncs.py", output_file="polarfuncs_compiled%{ext}")
