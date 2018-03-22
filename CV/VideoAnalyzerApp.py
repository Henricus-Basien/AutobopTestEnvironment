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

from functools import partial

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
        
        self.Labels["Flow"] = Label(text="Flow Data",pos_hint={'x':0,'top':0.85} ,size_hint=[1.0,0.05])

        for label in self.Labels.values():
            self.add_widget(label)

        #+++++++++++++++++++++++++++++++++++++++++++
        # Time keeping
        #+++++++++++++++++++++++++++++++++++++++++++
        
        self.t0 = getTime()
        self.t  = getTime()

        self.dt_analysis = getTime()

    def AnalyzeFrame(self,frame):

        self.dt = getTime()-self.t
        self.t  = getTime()

        if self.dt!=0:
            freq = 1./self.dt
        else:
            freq = 0

        DT = self.t-self.t0

        TimeLabelText = "T: "+str(round(DT,1))+" s"+" | "+str(round(freq,1))+" Hz"
        if self.dt_analysis!=0:
            TimeLabelText+="\n"+"AnalysisTime: "+str(round(self.dt_analysis*1000,1))+"ms"
            TimeLabelText+="|"+str(round(1./self.dt_analysis,1))+"Hz"

        self.Labels["Time"].text = TimeLabelText

        #+++++++++++++++++++++++++++++++++++++++++++
        # Get Sensor Data
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if UseAccelerometer:
            #print "Reading Accelerometer"
            self.acc = accelerometer.acceleration
            acc_Total = np.sum(np.array(self.acc)**2)**0.5
            #print "acc: ",acc
            self.Labels["Accelerometer"].text = "Acceleration: "+str(np.round(self.acc,3))
            self.Labels["Accelerometer"].text+= "\n"#" "
            self.Labels["Accelerometer"].text+= "(Total: "+str(round(acc_Total,3))+")"
            self.Labels["Accelerometer"].text+= " [m/s²]"

        if UseGyroscope:
            #print "Reading Gyroscope" 
            self.rps = np.degrees(gyroscope.get_orientation())#rotation
            rps_Total = np.sum(np.array(self.rps)**2)**0.5
            #print "rps: ",rps
            self.Labels["Gyroscope"].text = "Rotational Velocity: "+str(np.round(self.rps,3))
            self.Labels["Gyroscope"].text+= "\n"#" "
            self.Labels["Gyroscope"].text+= "(Total: "+str(round(rps_Total,3))+")"
            self.Labels["Gyroscope"].text+= " [deg/s]"

        #+++++++++++++++++++++++++++++++++++++++++++
        # Show Optical Flow
        #+++++++++++++++++++++++++++++++++++++++++++
        
        if 1:
            res_new = (150,200) #(240*2,320 *2)#(320,240)#(120,160)#(160,120) # (320,240)
            #print frame.shape
            frame = cv2.resize(frame, res_new)#(100, 50)) 
            #print "After",frame.shape

        if hasattr(self,"OpticalFlowAnalyzer"):
            if hasattr(self,"frame_old"):
                frame_new = frame
                Mode = 3#2
                #FlowManipulationFunction = self.FlowManipulationFunction
                FlowManipulationFunction = partial(self.OpticalFlowAnalyzer.SubstractRotation,rps=self.rps)
                frame = self.OpticalFlowAnalyzer.ShowOpticalFlow1(frame_new,self.frame_old,Mode=Mode,InvertColor=False,FlowManipulationFunction=FlowManipulationFunction)
                self.frame_old = frame_new
            else:
                self.frame_old = frame

            #-------------------------------------------
            # Get Flow Data
            #-------------------------------------------

            if hasattr(self.OpticalFlowAnalyzer,"flow"):
                self.Labels["Flow"].text = "Flow Data: "

                flows  = [self.OpticalFlowAnalyzer.flow,self.OpticalFlowAnalyzer.flow_corrected]
                flows.append(flows[1]-flows[0])
                titles = ["Original","Corrected","Dif"]
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

                #-------------------------------------------
                # Get Outliers
                #-------------------------------------------
            
                if 1:
                    flow_outliers = self.OpticalFlowAnalyzer.flow_corrected

                    #--- Substract Mean ---
                    for i in range(2):
                        Mean = np.mean(flow_outliers[:,:,i])
                        flow_outliers[:,:,i]-=Mean

                    #--- Get Total ---
                    flow_mag = np.linalg.norm(flow_outliers,axis=2)

                    #--- Show Outliers ---
                    step=5
                    threshold = 10
                    for i in range(0,flow_mag.shape[0],step):
                        #if i%step!=0:
                        #    continue
                        for j in range(0,flow_mag.shape[1],step):
                            #if j%step!=0:
                            #    continue
                            radius = 1
                            pt = (j,i)
                            
                            #print "flow_mag[i,j]",flow_mag[i,j]
                            if abs(flow_mag[i,j])>threshold:#1:
                                cv2.circle(frame,pt,radius,(0,120,0),-1)

        self.dt_analysis = getTime()-self.t

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

