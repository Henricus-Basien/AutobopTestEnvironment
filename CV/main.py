# -*- coding: utf-8 -*-

'''
Created on Friday 16.03.2018
Copyright Henricus N. Basien
Author: Henricus N. Basien
Email: Henricus@Basien.de
'''

#****************************************************************************************
# Imports
#****************************************************************************************

#+++++++++++++++++++++++++++++++++++++++++++
# External
#+++++++++++++++++++++++++++++++++++++++++++

import traceback,sys

#+++++++++++++++++++++++++++++++++++++++++++
# Internal
#+++++++++++++++++++++++++++++++++++++++++++

print "Started Importing OpticalAvoiderApp..."
try:
    from OpticalAvoiderApp import OpticalAvoiderApp
except:
    print "Import Failed"
    print '-'*60
    traceback.print_exc(file=sys.stdout)
    print '-'*60 
    quit()  

#****************************************************************************************
# Test Code
#****************************************************************************************

if __name__=="__main__":
    print "Running OpticalAvoiderApp..."
    OpticalAvoiderApp().run()
