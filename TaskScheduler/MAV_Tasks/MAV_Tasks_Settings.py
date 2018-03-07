# -*- coding: utf-8 -*-

'''
Created on Friday 02.03.2018
Copyright Henricus N. Basien
Author: Henricus N. Basien
Email: Henricus@Basien.de
'''

#****************************************************************************************
# Imports
#****************************************************************************************

from collections import OrderedDict

#****************************************************************************************
# Settings
#****************************************************************************************

#+++++++++++++++++++++++++++++++++++++++++++
# User
#+++++++++++++++++++++++++++++++++++++++++++

if 1:#0:#1:
    User = "SysAdministrator"#"Henricus N. Basien"
else:
    User = None

#+++++++++++++++++++++++++++++++++++++++++++
# SpecialContainerSettings
#+++++++++++++++++++++++++++++++++++++++++++

SpecialContainerSettings = OrderedDict()#dict()
SpecialContainerSettings["Active"]           = True
SpecialContainerSettings["ToDo"]             = True
SpecialContainerSettings["Priority"]         = "All"#5
SpecialContainerSettings["OldUnfinished"]    = True
SpecialContainerSettings["Misconfigured"]    = True
SpecialContainerSettings["TaskTypes"]        = True
SpecialContainerSettings["RecentlyFinished"] = 7
SpecialContainerSettings["Users"]            = 500#50
SpecialContainerSettings["SearchTool"]       = True
