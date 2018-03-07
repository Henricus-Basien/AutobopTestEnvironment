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

#+++++++++++++++++++++++++++++++++++++++++++
# External
#+++++++++++++++++++++++++++++++++++++++++++

import sys
sys.path.insert(0,"../TS.SPP")

#+++++++++++++++++++++++++++++++++++++++++++
# Internal
#+++++++++++++++++++++++++++++++++++++++++++

from Task import PrintSchedulerLegend
from TaskViewerApp import TaskViewerApp

#****************************************************************************************
# Visualization Init
#****************************************************************************************

ScaleFactor = 1.5#2#1.5#2#1#2 # Scaling the whole UI Interface
TV_size_hint = [0.125,0.04]

#+++++++++++++++++++++++++++++++++++++++++++
# Graphics Settings
#+++++++++++++++++++++++++++++++++++++++++++

from kivy.core.window import Window
Window.fullscreen = False#"auto"#False#True

#-------------------------------------------
# Set Default Sizes (based on Scale)
#-------------------------------------------

from DefaultTaskWidgets import default_size,SetDefaultFontSize
SetDefaultFontSize(default_size*ScaleFactor)

#****************************************************************************************
# Load Task&Team Data
#****************************************************************************************

from MAV_Tasks_Settings import User,SpecialContainerSettings

#========================================================================================
# Team
#========================================================================================

from MAV_Contributors import MAV_FullTeam
MAV_FullTeam.PrintInfo()
    
#========================================================================================
# Tasks
#========================================================================================

import MAV_Contributors
from Task import Load_Tasks
MAV_Tasks = Load_Tasks("Autonomous_Drone.Tasks",Team=MAV_FullTeam,Modules=[MAV_Contributors.__name__])

if __name__=="__main__":
    if 0:#1:
        PrintSchedulerLegend()
        MAV_Tasks.Process_and_Report()
    else:
        MAV_Tasks.Process()

    #+++++++++++++++++++++++++++++++++++++++++++
    # Print Tasks Data
    #+++++++++++++++++++++++++++++++++++++++++++

    if 1:
        SortingMethod = "AbsolutePriorityLevel"
        PrintData = True

        # MAV_Tasks.GetPriorityTasks(6,SortingMethod=SortingMethod,PrintData=PrintData)
        if 0: MAV_Tasks.GetPriorityTasks(5,SortingMethod=SortingMethod,PrintData=PrintData)
        # MAV_Tasks.GetPriorityTasks(4,SortingMethod=SortingMethod,PrintData=PrintData)
        # MAV_Tasks.GetShortPriorityTasks(PrintData=PrintData)
        # MAV_Tasks.GetToDoList_Now(PrintData=PrintData)
        # MAV_Tasks.GetMisConfiguredTasks(PrintData=PrintData)
        # MAV_Tasks.GetOldUnfinishedTasks(PrintData=PrintData)

    #****************************************************************************************
    # Run App
    #****************************************************************************************

    app = TaskViewerApp(MAV_Tasks,title="Autonomous Drone Tasks",User=User,SpecialContainerSettings=SpecialContainerSettings,ScaleFactor=ScaleFactor,TV_size_hint=TV_size_hint)
    app.run()
else:   
    MAV_Tasks.Process()