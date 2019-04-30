'''where you can set absolute and relative path used in the package'''
import os
import numpy as np

root = os.path.dirname(os.path.abspath(__file__))
F0_file =  os.path.join(root, '../aux/Thuillier_2003_0.3nm.dat')

