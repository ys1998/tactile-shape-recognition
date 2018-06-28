# -*- coding: utf-8 -*-
'''
#-------------------------------------------------------------------------------
# NATIONAL UNIVERSITY OF SINGAPORE - NUS
# SINGAPORE INSTITUTE FOR NEUROTECHNOLOGY - SINAPSE
# Singapore
# URL: http://www.sinapseinstitute.org
#-------------------------------------------------------------------------------
# Neuromorphic Engineering Group
# Author: Andrei Nakagawa-Silva, MSc
# Contact: nakagawa.andrei@gmail.com
#-------------------------------------------------------------------------------
# Description: GUI for testing the control of the iLimb
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
import os, sys, glob
sys.path.append('../shape_recognition/libraries/general')
sys.path.append('../shape_recognition/libraries/iLimb')
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from serialhandler import * #list serial ports
from iLimb import * #iLimb controller
#-------------------------------------------------------------------------------
Ui_MainWindow, QMainWindow = loadUiType('formiLimb_gui.ui')
#-------------------------------------------------------------------------------
class FormiLimb(QMainWindow, Ui_MainWindow):
    def __init__(self,_parent=None):
        super(FormiLimb,self).__init__()
        self.setupUi(self)
        self.init() #initialize the GUI

    def init(self):
        #creating GUI variables
        self.currentPwm = [0]*7
        self.currentPos = [0]*7
        #creating the GUI events
        #connect to serial port
        self.btnSerialConnect.clicked.connect(self.doConnect)
        #control the fingers
        self.btnControlFingers.clicked.connect(self.doControlFingers)
        #send pose
        self.btnPoses.clicked.connect(self.doSetPose)
        #populate the GUI
        #serial ports
        #find the available serial ports
        res = list_serial_ports()
        #add the serial ports to the combo box
        self.cbSerialPort.addItems(res)
        #create a list with all the comboBox related to commands that can be sent to the iLimb
        self.cbCmds = [self.cbThumb,self.cbIndex,self.cbMiddle,self.cbRing,self.cbLittle,self.cbThumbRotator,self.cbWrist]
        #create a list with all the checkbox related to the fingers
        self.chFingers = [self.chThumb,self.chIndex,self.chMiddle,self.chRing,self.chLittle,self.chThumbRotator,self.chWrist]
        #create a list with all the spinbox related to the fingers
        self.spFingers = [self.spThumb,self.spIndex,self.spMiddle,self.spRing,self.spLittle,self.spThumbRotator,self.spWrist]
        #gets the names of the fingers
        fings = []
        [fings.append(x) for x in iLimb.fingers.keys()]
        #rename the checkbox according to the names of the fingers in the class
        for i in range(len(self.chFingers)):
            self.chFingers[i].setText(fings[i])
        #iLimb control parameters
        #get all the keys related to commands that can be sent to the iLimb
        cmds = []
        [cmds.append(x) for x in iLimb.cmds.keys()] #creating the list with the commands
        for cb in self.cbCmds:
            if cb != self.cbWrist: #if not wrist put the first three commands
                #add the commands
                cb.addItems(cmds[0:4])
                #create event for all the combobox related to commands to the fingers
                cb.currentIndexChanged.connect(self.doUpdatePwmPos)
            else: #if wrist, put the two last commands
                cb.addItems(cmds[4:6])
        #create a list with all the poses that can be sent to the iLimb
        poses = []
        [poses.append(x) for x in iLimb.poses.keys()] #creating the list with the poses
        #add the poses to the combobox
        self.cbPoses.addItems(poses)

    def doConnect(self):
        self.iLimbCont = iLimbController(self.cbSerialPort.currentText())
        self.iLimbCont.connect()

    def doControlFingers(self):
        #retrieve the selected fingers from the checkbox
        fings = []
        #find the index of the checkbox that is checked inside the vector of checkbox objects
        [fings.append(self.chFingers.index(x)) if x.isChecked() else [] for x in self.chFingers]
        #retrieve the commands and the pwm/pos
        f = []
        cmds = []
        pwmpos = []
        for i in range(len(fings)):
            idx = fings[i]
            f.append(self.chFingers[idx].text())
            cmds.append(self.cbCmds[idx].currentText())
            pwmpos.append(self.spFingers[idx].value())
            if cmds[-1] == 'position':
                self.currentPos[idx] = pwmpos[-1]
            else:
                self.currentPwm[idx] = pwmpos[-1]
                self.currentPos[idx] = 0
        self.iLimbCont.control(f,cmds,pwmpos)
        #debugging
        #print(f,cmds,pwmpos,self.currentPos,self.currentPwm)

    def doSetPose(self):
        #send the pose to the iLimb
        self.iLimbCont.setPose(self.cbPoses.currentText())

    def doUpdatePwmPos(self,e):
        #retrieve the sender of the event
        sender = self.sender()
        #find the index of the sender
        idx = self.cbCmds.index(sender)
        #given the index, the proper spinbox can be updated
        #check whether it is a position command
        #if not position, then the spinbox will be pwm
        if sender.currentText() != 'position':
            self.spFingers[idx].setValue(self.currentPwm[idx])
            self.spFingers[idx].setMaximum(297)
        else: #otherwise, the spinbox will be position
            self.spFingers[idx].setValue(self.currentPos[idx])
            if idx < 5:
                self.spFingers[idx].setMaximum(500)
            elif idx == 5:
                self.spFingers[idx].setMaximum(750)
            else:
                self.spFingers[idx].setMaximum(360)

    def closeEevnt(self,event):
        print('closing')
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    from PyQt5 import QtCore, QtGui, QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    main = FormiLimb()
    main.show()
    sys.exit(app.exec_())
