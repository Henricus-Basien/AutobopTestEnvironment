# -*- coding: utf-8 -*-

'''
Created on  Friday 26.01.2018 - Monday 26.02.2018
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

#-------------------------------------------
# Kivy
#-------------------------------------------

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
#from kivy.uix.label import Label

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.slider import Slider

#+++++++++++++++++++++++++++++++++++++++++++
# Internal
#+++++++++++++++++++++++++++++++++++++++++++

try:
    from DefaultTaskWidgets import DefaultLabel as Label
except:
    from kivy.uix.label import Label

#****************************************************************************************
# Labeled Switch
#****************************************************************************************

class LabeledSwitch(BoxLayout):

    def __init__(self,text,color=[1]*4,pos_hint={"x":0,"y":0},size_hint=[1,1],*args,**kwargs):

        super(LabeledSwitch,self).__init__(pos_hint=pos_hint,size_hint=size_hint,*args,**kwargs)

    #    self.Initialize(*args,**kwargs)

    #def Initialize(self,*args,**kwargs):
        self.Label = Label(text=text,color=color)
        self.add_widget(self.Label)
        self.Switch = Switch(*args,**kwargs)
        self.add_widget(self.Switch)
        #print self.size, self.Switch.size

    def bindSwitch(self,*args,**kwargs):
        return self.Switch.bind(*args,**kwargs)

    def IsActive(self):
        return self.Switch.active

#****************************************************************************************
# Labeled Slider
#****************************************************************************************

class LabeledSlider(RelativeLayout):

    def __init__(self,text,color=[1]*4,pos_hint={"x":0,"y":0},size_hint=[1,1],*args,**kwargs):

        self.text = text

        super(LabeledSlider,self).__init__(pos_hint=pos_hint,size_hint=size_hint,*args,**kwargs)

    #    self.Initialize(*args,**kwargs)

    #def Initialize(self,*args,**kwargs):
        self.Label = Label(text=text,color=color,pos_hint={"center_x":0.5,"top":1.5})
        self.add_widget(self.Label)
        self.Slider = Slider(*args,**kwargs)
        self.add_widget(self.Slider)
        #print self.size, self.Slider.size

        self.bindSlider(value=self.UpdateLabel)
        self.UpdateLabel()

    def UpdateLabel(self,*args,**kwargs):

        self.Label.text = self.text+": "+str(round(self.Slider.value,2))

    def bindSlider(self,*args,**kwargs):
        return self.Slider.bind(*args,**kwargs)

    def GetValue(self):
        return self.Slider.value