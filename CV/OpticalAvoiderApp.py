# -*- coding: utf-8 -*-

'''
Created on Friday 13.03.2018
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

import os,sys,traceback

import time
from time import time as getTime

from functools import partial

from copy import copy

from collections import OrderedDict

#-------------------------------------------
# Mathematics
#-------------------------------------------

import numpy as np

#-------------------------------------------
# Kivy
#-------------------------------------------

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.button import Button
from kivy.uix.label import Label
#from kivy.uix.slider import Slider

#-------------------------------------------
# Computer Vision
#-------------------------------------------

import cv2

#-------------------------------------------
# Android
#-------------------------------------------
print "Importing Plyer"
UseAccelerometer = False#True
if UseAccelerometer:
    from plyer import accelerometer

UseGyroscope = True
if UseGyroscope:
    from plyer import gyroscope
print "Done importing Plyer"

#from plyer import orientation

#+++++++++++++++++++++++++++++++++++++++++++
# Internal
#+++++++++++++++++++++++++++++++++++++++++++

from AndroidCamera import CustomCameraOpenCV
from OpticalAvoider import OpticalAvoider

from LabeledSwitch import LabeledSwitch,LabeledSlider

ProfilerPath = os.path.join(os.path.split(__file__)[0],"Profiler")
sys.path.insert(0,ProfilerPath)
#from Profiler import Profiler
try:
    from Profiler import Profiler
    ProfilerImported = True
except:
    ProfilerImported = False
    print "WARNING: Failed to import Profiler!"
    traceback.print_exc(file=sys.stdout)

#========================================================================================
# Logging
#========================================================================================

if 0:
    #Use these lines to see all the messages
    from kivy.logger import Logger
    import logging
    Logger.setLevel(logging.TRACE)

#****************************************************************************************
# Camera Analyzer
#****************************************************************************************

class AndroidOpenCV_OpticalAvoider(CustomCameraOpenCV,FloatLayout):
    def __init__(self, *args,**kwargs):

        print "Building Analyzer"
        
        super(AndroidOpenCV_OpticalAvoider,self).__init__(*args,**kwargs)

        #--- Optical Avoider ---
        self.OpticalAvoider = OpticalAvoider()

        #-------------------------------------------
        # Sensor Data
        #-------------------------------------------
        
        self.InitializeSensors()

        #+++++++++++++++++++++++++++++++++++++++++++
        # Labels
        #+++++++++++++++++++++++++++++++++++++++++++
        
        self.InitializeLabels()

        #+++++++++++++++++++++++++++++++++++++++++++
        # Controls
        #+++++++++++++++++++++++++++++++++++++++++++
        
        self.InitializeControls()

        #+++++++++++++++++++++++++++++++++++++++++++
        # Time keeping
        #+++++++++++++++++++++++++++++++++++++++++++
        
        self.InitializeTimeKeeping()

    def InitializeSensors(self):
        print "Intializing Sensors"
        #--- Accelerometer Data ---
        if UseAccelerometer:
            print "Enable Accelerometer"
            print accelerometer
            accelerometer.enable()
            print "Accelerometer Enabled"

        #--- Gyroscope Data ---
        if UseGyroscope:
            print "Enable Gyroscope"
            print gyroscope
            gyroscope.enable()
            print "Gyroscope Enabled"

    def InitializeLabels(self):
        self.Labels = dict()
        self.Labels["Gyroscope"]     = Label(text="Gyroscope Data"    ,pos_hint={'x':0,'y':0}  ,size_hint=[1.0,0.05])
        self.Labels["Accelerometer"] = Label(text="Accelerometer Data",pos_hint={'x':0,'y':0.05},size_hint=[1.0,0.05])

        self.Labels["Time"] = Label(text="Time Data",pos_hint={'x':0,'top':1.0}  ,size_hint=[1.0,0.05])
        
        self.Labels["Flow"] = Label(text="Flow Data",pos_hint={'x':0,'top':0.85} ,size_hint=[1.0,0.05])

        self.Labels["Control"] = Label(text="Control Info",pos_hint={'x':0,'top':0.925} ,size_hint=[1.0,0.05])

        for label in self.Labels.values():
            self.add_widget(label)

    def InitializeControls(self):

        self.InitializeBooleanControl()
        self.InitializeVariableControl()

    def InitializeBooleanControl(self):
        size_hint = [0.5,0.3]#[0.4,0.15]
        self.BooleanControlLayout = BoxLayout(pos_hint={'right':1.0,'center_y':0.5},size_hint=size_hint,orientation="vertical")

        self.BooleanControls = OrderedDict()
        for Setting in self.OpticalAvoider.BooleanSettings.keys():
            self.BooleanControls[Setting] = LabeledSwitch(text=Setting ,active = self.OpticalAvoider.BooleanSettings[Setting])
            self.BooleanControls[Setting].bindSwitch(active=partial(self.SetBooleanSetting_Callback,Setting=Setting))

        for widget in self.BooleanControls.values():
            self.BooleanControlLayout.add_widget(widget)

        self.add_widget(self.BooleanControlLayout)

    def InitializeVariableControl(self):
        size_hint = [1.0,0.1]
        self.VariableControlLayout = BoxLayout(pos_hint={'center_x':0.5,'y':0.1},size_hint=size_hint,orientation="vertical")

        self.VariableControls = OrderedDict()
        for Setting in self.OpticalAvoider.VariableSettings.keys():
            Val,Min,Max = self.OpticalAvoider.VariableSettings[Setting]
            self.VariableControls[Setting] = LabeledSlider(text=Setting,value=Val,min=Min,max=Max)
            self.VariableControls[Setting].bindSlider(value=partial(self.SetVariableSetting_Callback,Setting=Setting))

        for widget in self.VariableControls.values():
            self.VariableControlLayout.add_widget(widget)

        self.add_widget(self.VariableControlLayout)

    def SetBooleanSetting_Callback(self,instance, value,Setting=None):

        #Setting = instance.Label.text
        self.OpticalAvoider.BooleanSettings[Setting] = value

    def SetVariableSetting_Callback(self,instance, value,Setting=None):

        #print instance,value,Setting

        self.OpticalAvoider.VariableSettings[Setting][0] = value

    def InitializeTimeKeeping(self):
        self.t0 = getTime()
        self.t  = getTime()

        self.dt_analysis = getTime()

    def TrackTime(self):
        self.dt = getTime()-self.t
        self.t  = getTime()

        if self.dt!=0:
            self.freq = 1./self.dt
        else:
            self.freq = 0

        self.DT = self.t-self.t0

        self.ShowTimeText()

    def ShowTimeText(self):
        TimeLabelText = "T: "+str(round(self.DT,1))+" s"+" | "+str(round(self.freq,1))+" Hz"
        if self.dt_analysis!=0:
            if self.orientation=="portrait": TimeLabelText+="\n"
            TimeLabelText+="AnalysisTime: "+str(round(self.dt_analysis*1000,1))+"ms"
            TimeLabelText+="|"+str(round(1./self.dt_analysis,1))+"Hz"

        self.Labels["Time"].text = TimeLabelText

    #========================================================================================
    # Analyze Frame
    #========================================================================================

    def AnalyzeFrame(self,frame,Profile=False):#True):

        #print "orientation",self.orientation

        if Profile:
            if ProfilerImported:
                function = partial(self.AnalyzeFrame,frame,Profile=False)
                return Profiler.Profile(function,FileName="VideoAnalysis.pstats",AutoVisualize=False,PrintInfo=True,PrintStats=True,PrintTime=True)
            else:
                print "Unable to Profile, Profiler could not be imported!"

        self.TrackTime()

        #+++++++++++++++++++++++++++++++++++++++++++
        # Get Sensor Data
        #+++++++++++++++++++++++++++++++++++++++++++
        
        self.GetIMUData()

        #+++++++++++++++++++++++++++++++++++++++++++
        # Run OpticalAvoider
        #+++++++++++++++++++++++++++++++++++++++++++
        
        frame = self.OpticalAvoider.AnalyzeFrame(frame,self.dt,rps=self.rps)

        #+++++++++++++++++++++++++++++++++++++++++++
        # Show Optical Flow
        #+++++++++++++++++++++++++++++++++++++++++++

        if hasattr(self.OpticalAvoider.OpticalFlowAnalyzer,"flow"):
            if 1:
                self.ShowFlowData()

        self.dt_analysis = getTime()-self.t

        return frame

    #========================================================================================
    # Flow Data
    #========================================================================================

    def ShowFlowData(self):

        OFA = self.OpticalAvoider.OpticalFlowAnalyzer

        self.Labels["Flow"].text = "Optical Flow Data: "

        flows  = [OFA.flow]
        titles = ["Original"]

        if self.OpticalAvoider.BooleanSettings["DeRotateFlow"]:
            flows.append(OFA.flow_corrected)
            flows.append(flows[1]-flows[0])
            titles += ["Corrected","Dif"]

        for i in range(len(flows)):
            flow  = flows[i]
            title = titles[i]

            flow_mag = np.linalg.norm(flow,axis=2)
            Mean = np.mean(flow_mag)
            Min  = np.min(flow_mag)
            Max  = np.max(flow_mag)
            self.Labels["Flow"].text+="\n"+title+": "
            self.Labels["Flow"].text+= "Mean="+str(round(Mean,2))
            self.Labels["Flow"].text+= ","+"Min=" +str(round(Min ,2))
            self.Labels["Flow"].text+= ","+"Max=" +str(round(Max ,2))


        if 0:#1:
            self.Labels["Control"].text = "Control Data: "
            if hasattr(self.OpticalAvoider,"OptColumn"):
                self.Labels["Control"].text+= "Column="+str(self.OpticalAvoider.OptColumn)
                self.Labels["Control"].text+= ","
                self.Labels["Control"].text+= "Row="+str(self.OpticalAvoider.OptRow)

    #========================================================================================
    # IMU Data
    #========================================================================================
    
    def GetIMUData(self,WriteLabels=True):

        if UseAccelerometer:
            #print "Reading Accelerometer"
            self.acc = accelerometer.acceleration
            self.acc_Total = np.sum(np.array(self.acc)**2)**0.5
            #print "acc: ",acc
        if UseGyroscope:
            #print "Reading Gyroscope" 
            self.rps = np.degrees(gyroscope.get_orientation())#rotation
            self.rps_Total = np.sum(np.array(self.rps)**2)**0.5
            #print "rps: ",rps

        if WriteLabels:
            self.WriteIMU_Labels()

    def WriteIMU_Labels(self):

        if UseAccelerometer:
            self.Labels["Accelerometer"].text = "Acceleration: "+str(np.round(self.acc,3))
            if self.orientation=="portrait": self.Labels["Accelerometer"].text+= "\n"#" "
            self.Labels["Accelerometer"].text+= "(Total: "+str(round(self.acc_Total,3))+")"
            self.Labels["Accelerometer"].text+= " [m/s²]"

        if UseGyroscope:
            self.Labels["Gyroscope"].text = "Rotational Velocity: "+str(np.round(self.rps,3))
            if self.orientation=="portrait": self.Labels["Gyroscope"].text+= "\n"#" "
            self.Labels["Gyroscope"].text+= "(Total: "+str(round(self.rps_Total,3))+")"
            self.Labels["Gyroscope"].text+= " [deg/s]"

#****************************************************************************************
# Camera Analyzer Test Code
#****************************************************************************************
"""
class CameraAnalyzer_Android(BoxLayout):

    def __init__(self,*args,**kwargs):

        super(CameraAnalyzer_Android,self).__init__(*args,**kwargs)

        self.orientation = "vertical"

        Resolution = (320,240)#(160,120)#(320,240)#(1280,720)#(640,480)

        #self.camera = CustomCamera(resolution=Resolution,play=True)
        #self.add_widget(self.camera)

        self.camera = CustomCameraOpenCV_Analyzer(size=Resolution,resolution=Resolution,play=True)
        self.add_widget(self.camera)
"""
class OpticalAvoiderApp(App):

    def build(self):
        print "Starting Build!"

        Resolution = (320,240)#(640,480)#(480,640)#(640,480)#(240,320) # (320,240)#(160,120)#(320,240)#(1280,720)#(640,480)

        return AndroidOpenCV_OpticalAvoider(size=Resolution,resolution=Resolution,play=True) #CameraAnalyzer_Android()

#****************************************************************************************
# Test Code
#****************************************************************************************

if __name__=="__main__":
    print "Running OpticalAvoiderApp..."
    OpticalAvoiderApp().run()

