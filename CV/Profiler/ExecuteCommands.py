# -*- coding: utf-8 -*-

'''
Created on: 5.10.2016
Copyright:  MonkeyWings B.V.
Author:     Henricus N. Basien
Email:      H.Basien@MonkeyWings.nl
'''

#==========================================================
# Imports
#==========================================================

import os
import subprocess as sp
from timeit import default_timer as getTime

#==========================================================
# Execute System Command
#==========================================================

def ExeCmd(cmd,RunAsRoot=False,PrintCmd=False,PrintOutput=False,Shell=False):

    cmds = cmd.split(" ")
    if RunAsRoot:
        cmds.insert(0, '/usr/bin/pkexec')
        cmd = " ".join(cmds)

    if PrintCmd:
        print "-"*max(50,len(cmd)+35)#50
        print ">"*3+"Executing terminal command: '"+cmd+"'"
        print "-"*max(50,len(cmd)+35)#50
    

    if 1:
        try:
            
                            
            p = sp.Popen(cmds,stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE,shell=Shell)
            output, errors = p.communicate()
            if PrintOutput:
                print "Output:"+"\n",output
                print "Errors:"+"\n",errors
            return output
        except:
            print ">"*3+"An Error Occured during the execution of this command!"
            raise
    else:
        try:
            os.system(cmd)
        except:
            print ">"*3+"An Error Occured during the execution of this command!"
            raise

def ExecuteCommands(cmds,sudo=False,PrintCmd=False,PrintOutput=False,TimeIt=False):

    if TimeIt:
        Times = []
        t00 = getTime()

    for cmd in cmds:
        if sudo:
            cmd = "sudo "+cmd

        if TimeIt:
            t0 = getTime()
        ExeCmd(cmd,PrintCmd=PrintCmd,PrintOutput=PrintOutput)
        if TimeIt:
            t = getTime()-t0
            Times.append(t)
            print ">/> Time passed: "+str(round(t,2))+" s"

    if TimeIt:
        print "="*50
        print "Total Runtime: "+str(round(getTime()-t00,2))+" s:"
        for i in range(len(cmds)):
            print " "*3+str(round(Times[i],2))+" s: "+'"'+cmds[i]+'"'
        

#==========================================================
# Test Code
#==========================================================

if __name__=="__main__":
    msg = "Hello World"
    cmd = "echo "+'"'+msg+'"'

    Shell = False#True

    ExeCmd(cmd,PrintCmd=True,PrintOutput=True,Shell=Shell,TimeIt=True)
