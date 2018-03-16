# -*- coding: utf-8 -*-

'''
Created on Friday 13.03.2018
Copyright Henricus N. Basien
Author: Henricus N. Basien
Email: Henricus@Basien.de
'''

'''@package 
Description: 
'''

#****************************************************************************************
# Imports
#****************************************************************************************

#+++++++++++++++++++++++++++++++++++++++++++
# External
#+++++++++++++++++++++++++++++++++++++++++++

import time
from time import time as getTime

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

#-------------------------------------------
# Computer Vision
#-------------------------------------------

import cv2

#-------------------------------------------
# Android
#-------------------------------------------
print "Importing Plyer"
UseAccelerometer = True
if UseAccelerometer:
    from plyer import accelerometer

UseGyroscope = True
if UseGyroscope:
    from plyer import gyroscope
print "Done importing Plyer"

#+++++++++++++++++++++++++++++++++++++++++++
# Internal
#+++++++++++++++++++++++++++++++++++++++++++

from AndroidCamera import CustomCameraOpenCV
from OpticalFlowAnalyzer import OpticalFlowAnalyzer

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

class CustomCameraOpenCV_Analyzer(CustomCameraOpenCV,FloatLayout):
    def __init__(self, *args,**kwargs):

        print "Building Analyzer"
        
        super(CustomCameraOpenCV_Analyzer,self).__init__(*args,**kwargs)

        #--- Optical Flow ---
        self.OpticalFlowAnalyzer = OpticalFlowAnalyzer()

        #-------------------------------------------
        # Sensor Data
        #-------------------------------------------
        
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

        #+++++++++++++++++++++++++++++++++++++++++++
        # Labels
        #+++++++++++++++++++++++++++++++++++++++++++
        
        self.Labels = dict()
        self.Labels["Gyroscope"]     = Label(text="Gyroscope Data"    ,pos_hint={'x':0,'y':0}  ,size_hint=[1.0,0.05])
        self.Labels["Accelerometer"] = Label(text="Accelerometer Data",pos_hint={'x':0,'y':0.05},size_hint=[1.0,0.05])

        self.Labels["Time"] = Label(text="Time Data",pos_hint={'x':0,'top':1.0}  ,size_hint=[1.0,0.05])

        for label in self.Labels.values():
            self.add_widget(label)

        #+++++++++++++++++++++++++++++++++++++++++++
        # Time keeping
        #+++++++++++++++++++++++++++++++++++++++++++
        
        self.t0 = getTime()
        self.t  = getTime()

    def AnalyzeFrame(self,frame):

        self.dt = getTime()-self.t
        self.t  = getTime()

        if self.dt!=0:
            freq = 1./self.dt
        else:
            freq = 0

        DT = self.t-self.t0
        self.Labels["Time"].text = "T: "+str(round(DT,1))+" s"+" | "+str(round(freq,1))+" Hz"

        #+++++++++++++++++++++++++++++++++++++++++++
        # Get Sensor Data
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if UseAccelerometer:
            #print "Reading Accelerometer"
            acc = accelerometer.acceleration
            #print "acc: ",acc
            self.Labels["Accelerometer"].text = "Accleration: "+str(np.round(acc,3))

        if UseGyroscope:
            #print "Reading Gyroscope" 
            rps = gyroscope.get_orientation()#rotation
            #print "rps: ",rps
            self.Labels["Gyroscope"].text = "Rotational Velocity: "+str(np.round(rps,3))

        #+++++++++++++++++++++++++++++++++++++++++++
        # Show Optical Flow
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if hasattr(self,"OpticalFlowAnalyzer"):
            if hasattr(self,"frame_old"):
                frame_new = frame
                Mode = 3#2
                frame = self.OpticalFlowAnalyzer.ShowOpticalFlow1(frame_new,self.frame_old,Mode=Mode,InvertColor=False)
                self.frame_old = frame_new
            else:
                self.frame_old = frame
        return frame

#****************************************************************************************
# Camera Analyzer Test Code
#****************************************************************************************

class CameraAnalyzer_Android(BoxLayout):

    def __init__(self,*args,**kwargs):

        super(CameraAnalyzer_Android,self).__init__(*args,**kwargs)

        self.orientation = "vertical"

        Resolution = (320,240)#(160,120)#(320,240)#(1280,720)#(640,480)

        #self.camera = CustomCamera(resolution=Resolution,play=True)
        #self.add_widget(self.camera)

        self.camera = CustomCameraOpenCV_Analyzer(size=Resolution,resolution=Resolution,play=True)
        self.add_widget(self.camera)

class VideoAnalyzerApp(App):

    def build(self):
        print "Starting Build!"
        return CameraAnalyzer_Android()

#****************************************************************************************
# Test Code
#****************************************************************************************

if __name__=="__main__":
    print "Running VideoAnalyzerApp..."
    VideoAnalyzerApp().run()

