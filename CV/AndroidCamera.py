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

#-------------------------------------------
# Kivy
#-------------------------------------------

from kivy.core.camera.camera_android import CameraAndroid # as CoreCamera
CoreCamera = CameraAndroid
from kivy.uix.camera import Camera

from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

from kivy.clock import Clock
from kivy.properties import BooleanProperty

from kivy.core.window import Window

#-------------------------------------------
# Image Processing
#-------------------------------------------

import cv2
import imutils

#****************************************************************************************
# Android Camera
#****************************************************************************************

class OrientationChecker(object):

    def __init__(self,*args,**kwargs):

        self.CheckOrientation()

        Window.bind(size=self.CheckOrientation)

    def CheckOrientation(self,*args,**kwargs):
        if Window.size[0]>Window.size[1]:
            self.orientation = "landscape"
        else:
            self.orientation = "portrait"
        #print "orientation",self.orientation

class CustomCameraAndroid(CameraAndroid):

    def _update(self, dt):

        self._surface_texture.updateTexImage()
        self._refresh_fbo()
        if self._texture is None:
            self._texture = self._fbo.texture
            self.dispatch('on_load')
        self._copy_to_gpu()    

class CustomCamera(Camera):
    
    def _on_index(self, *largs):
        self._camera = None
        if self.index < 0:
            return
        if self.resolution[0] < 0 or self.resolution[1] < 0:
            return
        self._camera = CoreCamera(index=self.index,
                                  resolution=self.resolution, stopped=True)
        self._camera.bind(on_load=self._camera_loaded)
        if self.play:
            self._camera.start()
            self._camera.bind(on_texture=self.on_tex)

#****************************************************************************************
# Custom Camera OpenCV
#****************************************************************************************

class CustomCameraOpenCV(Image,OrientationChecker):

    allow_stretch = BooleanProperty(True)

    #========================================================================================
    # Initialization
    #========================================================================================
    
    def __init__(self, fps=30, *args,**kwargs):
        
        self.index = 0
        kwargs.setdefault('resolution', (640, 480))
        self.resolution = kwargs.get('resolution')

        super(CustomCameraOpenCV, self).__init__(*args,**kwargs)
        
        self.InitCapture()

        Clock.schedule_interval(self.update, 1.0 / fps)

    def InitCapture(self):

        #print "Initialized Camera!"*10

        if hasattr(self,"capture"):
            print "Removed Original Capture..."
            self.capture._release_camera()
            del self.capture
            time.sleep(1)

        self.capture = CoreCamera(index=self.index,resolution=self.resolution, stopped=True)

        #self.capture.bind(on_load=self.capture_loaded)
        self.play = True
        if self.play:
            self.capture.start()
            #self.capture.bind(on_texture=self.on_tex)

    #========================================================================================
    # Update
    #========================================================================================

    def update(self, dt=0):

        if 0:#1: #if self.orientation=="portrait":
            self.FlipOrientation()

        #frame = self.capture.read_frame()
        try:
            frame = self.capture.read_frame() #ret, frame = self.capture.read()
        except:
            frame = None

        #print "OpenCV frame:",frame
        if frame is not None:#ret:
            #print type(frame),frame.shape,self.size,self.size_hint
            #frame = frame.astype(int)

            #+++++++++++++++++++++++++++++++++++++++++++
            # Prepare Frame
            #+++++++++++++++++++++++++++++++++++++++++++

            frame = self.PrepareFrame(frame)

            #+++++++++++++++++++++++++++++++++++++++++++
            # Analyze Frame (if Set!)
            #+++++++++++++++++++++++++++++++++++++++++++
            
            frame = self.AnalyzeFrame(frame)
            
            #+++++++++++++++++++++++++++++++++++++++++++
            # Convert to Texture
            #+++++++++++++++++++++++++++++++++++++++++++
            
            texture = self.GetTexture(frame)

            #+++++++++++++++++++++++++++++++++++++++++++
            # Show Texture
            #+++++++++++++++++++++++++++++++++++++++++++
            
            self.ShowTexture(texture)

    def FlipOrientation(self):

        #self.capture.resolution = self.capture.resolution[::-1]
        self.resolution = self.resolution[::-1]
        self.InitCapture()

    #========================================================================================
    # Basic Frame Preparation & Texture Handling
    #========================================================================================

    def PrepareFrame(self,frame):
        #--- Change OpenCV BGR to RGB ---
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #--- Rotate Image by 90 degrees! ---
        if self.orientation=="portrait":
            frame = imutils.rotate_bound(frame, 90)#angle)

        #--- Flip Image Horizontally ---
        frame = cv2.flip(frame, 0)
        return frame

    def GetTexture(self,frame):
        if 1:
            buf = frame.tostring()
        else:
            buf = fra

        texture_res = (frame.shape[1], frame.shape[0])

        colorfmt='rgb'#'bgr'
        texture = Texture.create(size=texture_res, colorfmt=colorfmt)
        texture.blit_buffer(buf, colorfmt=colorfmt, bufferfmt='ubyte')
        return texture

    def ShowTexture(self,texture):
        #--- display image from the texture ---
        self.texture = texture

        #--- Draw Fullscreen Rectangle Image! ---
        if 0:
            with self.canvas:
                Rectangle(texture=self.texture, pos=self.pos, size=self.size)

    #========================================================================================
    # Dummy Analyze Frame Function
    #========================================================================================
    
    def AnalyzeFrame(self,frame):
        return frame