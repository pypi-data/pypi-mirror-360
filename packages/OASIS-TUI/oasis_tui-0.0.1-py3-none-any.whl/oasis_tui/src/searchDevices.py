'''
 searchDevices.py
 
	Class handling search of OASIS devices

  Copyright (c) 2025 Oliver Zobel - MIT License

  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
  to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
  IN THE SOFTWARE.
  
 '''

import serial
import serial.tools.list_ports
import time

from PyQt5 import QtGui

class searchDevices():
    def __init__(self):
        
        self.Devices = []
        
        return
        
    def SerialSearch(self, printLogSignal):
        
        self.Devices = []
        
        printLogSignal.emit("[OASIS-GUI]: Searching devices...\n")
        
        self.serialSpeed = 1000000
    
        # Search all available COM devices
        comlist = serial.tools.list_ports.comports()
        connected = []
        for element in comlist:
            connected.append(element.device)
        
        if connected:
            
            for DeviceNum in range(0, len(connected)):
                printLogSignal.emit("[OASIS-GUI]: Found device on port " + connected[DeviceNum] + "\n")
                
                # Connect to Serial Device
                try:
                    s = serial.Serial(port=connected[DeviceNum], baudrate=self.serialSpeed, timeout=2)
                except (OSError, serial.SerialException):
                    printLogSignal.emit("[OASIS-GUI]: DEVICE ERROR! Could not open serial communication on port " + connected[DeviceNum] + "\n\n")
                    continue
                
                while s.inWaiting():
                    SerialAnswer = s.readline()
                    if SerialAnswer !=bytes("","utf-8"):
                        if SerialAnswer.startswith(bytes("[OASIS]","utf-8")):
                            printLogSignal.emit(SerialAnswer.decode("utf-8",errors="ignore"))
                
                # Get Device Information
                s.write(bytes("OASIS.RawInfo()","utf-8"))
                printLogSignal.emit("[OASIS-GUI]: Getting device info...\n")
                DeviceInfo = s.readline().decode("utf-8",errors="ignore").split(";")

                s.close
                if(len(DeviceInfo)==8):
                    isOASIS = True
                    printLogSignal.emit("[OASIS-GUI]: Device on port " + connected[DeviceNum] + " is an OASIS board\n")
                else:
                    isOASIS = False
                    DeviceInfo = [""]
                    printLogSignal.emit("[OASIS-GUI]: Device on port " + connected[DeviceNum] + " is unknown or does not respond\n")
                
                self.Devices.append([connected[DeviceNum],DeviceInfo,isOASIS,self.serialSpeed])
            
        else:
            printLogSignal.emit("[OASIS-GUI]: Did not find any devices\n")
            
        return
    
    def UpdateDeviceList(self, Window):
        
        # Clear Device List Combobox
        Window.comboBox.clear()
        
        # No Devices found
        if(len(self.Devices)==0):
            
            Window.comboBox.setEnabled(False)
            Window.comboBox.addItem("No Devices")
            
        else:
            
            Window.comboBox.setEnabled(True)
            
            # Sort Devices (OASIS first)
            DevicesOASIS = []
            DevicesOther = []
            
            for Device in range(0,len(self.Devices)):
                if(self.Devices[Device][2]):
                    DevicesOASIS.append(self.Devices[Device])
                else:
                    DevicesOther.append(self.Devices[Device])
            
            Window.textEdit.append("[OASIS-GUI]: Found " + str(len(DevicesOASIS)) + " OASIS Board(s) and " + str(len(DevicesOther)) + " unknown device(s).\n")
            Window.textEdit.repaint()
            
            self.Devices = DevicesOASIS
            for i in range(0,len(DevicesOther)):
                self.Devices.append(DevicesOther[i])
            
            for Device in range(0,len(self.Devices)):
                
                # Device found is an OASIS
                if(self.Devices[Device][2]):
                    Window.comboBox.addItem(self.Devices[Device][1][6] + " V." + self.Devices[Device][1][0] + " - " + self.Devices[Device][1][5] + " (" + self.Devices[Device][0] + ")")
                else:
                    Window.comboBox.addItem("Unknown Device (" + self.Devices[Device][0] + ")")
            
            Window.comboBox.repaint()
            
        return
    
    def UpdateSelectedDevice(self, Window):
        
        DeviceSelected = Window.comboBox.currentIndex()
        
        Window.comboBox_2.clear()
        Window.comboBox_3.clear()
        Window.comboBox_4.clear()
        Window.comboBox_5.clear()
        Window.comboBox_6.clear()
        Window.comboBox_7.clear()
        Window.comboBox_8.clear()
        Window.comboBox_9.clear()
        Window.comboBox_10.clear()
        Window.comboBox_11.clear()
        
        # No Device found
        if(len(self.Devices)==0):
            Window.label_2.setPixmap(QtGui.QPixmap(":/Boards/resources/boards/Unknown.png"))
            Window.label_8.setText("")
            Window.label_9.setText("")
            Window.label_10.setText("")
            Window.label_11.setText("")
            Window.label_28.setText("")
            Window.checkBox.setChecked(False)
            Window.checkBox_2.setChecked(False)
            
            # Disable sampling
            Window.tabWidget.setEnabled(False)
            Window.pushButton_2.setEnabled(False)
            
        else:
            if(self.Devices[DeviceSelected][2]):
                
                # Update GUI Text
                Window.label_28.setText(self.Devices[DeviceSelected][1][6]) # Device architecture
                Window.label_8.setText(self.Devices[DeviceSelected][1][5]) # Device Name
                Window.label_9.setText(self.Devices[DeviceSelected][1][0]) # Hardware Version
                Window.label_10.setText(self.Devices[DeviceSelected][1][1]) # Firmware Version
                
                # Set available Voltage ranges
                if(self.Devices[DeviceSelected][1][2]=="18"):
                    Window.label_11.setText("AD7606C-18 (18 Bit resolution)")
                    Window.comboBox_11.setEnabled(True)
                    Window.comboBox_11.addItem("2.5")
                    Window.comboBox_11.addItem("5.0")
                    Window.comboBox_11.addItem("6.25")
                    Window.comboBox_11.addItem("10")
                    Window.comboBox_11.addItem("12.5")
                    Window.comboBox_2.setEnabled(True)
                    Window.comboBox_2.addItem("2.5")
                    Window.comboBox_2.addItem("5.0")
                    Window.comboBox_2.addItem("6.25")
                    Window.comboBox_2.addItem("10")
                    Window.comboBox_2.addItem("12.5")
                    Window.comboBox_3.setEnabled(True)
                    Window.comboBox_3.addItem("2.5")
                    Window.comboBox_3.addItem("5.0")
                    Window.comboBox_3.addItem("6.25")
                    Window.comboBox_3.addItem("10")
                    Window.comboBox_3.addItem("12.5")
                    Window.comboBox_4.setEnabled(True)
                    Window.comboBox_4.addItem("2.5")
                    Window.comboBox_4.addItem("5.0")
                    Window.comboBox_4.addItem("6.25")
                    Window.comboBox_4.addItem("10")
                    Window.comboBox_4.addItem("12.5")
                    Window.comboBox_5.setEnabled(True)
                    Window.comboBox_5.addItem("2.5")
                    Window.comboBox_5.addItem("5.0")
                    Window.comboBox_5.addItem("6.25")
                    Window.comboBox_5.addItem("10")
                    Window.comboBox_5.addItem("12.5")
                    Window.comboBox_6.setEnabled(True)
                    Window.comboBox_6.addItem("2.5")
                    Window.comboBox_6.addItem("5.0")
                    Window.comboBox_6.addItem("6.25")
                    Window.comboBox_6.addItem("10")
                    Window.comboBox_6.addItem("12.5")
                    Window.comboBox_7.setEnabled(True)
                    Window.comboBox_7.addItem("2.5")
                    Window.comboBox_7.addItem("5.0")
                    Window.comboBox_7.addItem("6.25")
                    Window.comboBox_7.addItem("10")
                    Window.comboBox_7.addItem("12.5")
                    Window.comboBox_8.setEnabled(True)
                    Window.comboBox_8.addItem("2.5")
                    Window.comboBox_8.addItem("5.0")
                    Window.comboBox_8.addItem("6.25")
                    Window.comboBox_8.addItem("10")
                    Window.comboBox_8.addItem("12.5")
                    Window.comboBox_9.setEnabled(True)
                    Window.comboBox_9.addItem("2.5")
                    Window.comboBox_9.addItem("5.0")
                    Window.comboBox_9.addItem("6.25")
                    Window.comboBox_9.addItem("10")
                    Window.comboBox_9.addItem("12.5")
                    Window.comboBox_10.setEnabled(True)
                    Window.comboBox_10.addItem("x1")
                    Window.comboBox_10.addItem("x2")
                    Window.comboBox_10.addItem("x4")
                    Window.comboBox_10.addItem("x8")
                    Window.comboBox_10.addItem("x16")
                    Window.comboBox_10.addItem("x32")
                    Window.comboBox_10.addItem("x64")
                    Window.comboBox_10.addItem("x128")
                    Window.comboBox_10.addItem("x256")
                    Window.comboBox_10.setCurrentIndex(2)
                elif(self.Devices[DeviceSelected][1][2]=="16"):
                    Window.label_11.setText("AD7606-4 (16 Bit resolution)")
                    Window.comboBox_2.setEnabled(True)
                    Window.comboBox_3.setEnabled(False)
                    Window.comboBox_4.setEnabled(False)
                    Window.comboBox_5.setEnabled(False)
                    Window.comboBox_2.addItem("5.0")
                    Window.comboBox_2.addItem("10.0")
                    Window.comboBox_3.addItem("5.0")
                    Window.comboBox_3.addItem("10.0")
                    Window.comboBox_4.addItem("5.0")
                    Window.comboBox_4.addItem("10.0")
                    Window.comboBox_5.addItem("5.0")
                    Window.comboBox_5.addItem("10.0")
                else:
                    Window.label_11.setText("Unknown ADC")
                
                # Detect Hardware Features
                if(self.Devices[DeviceSelected][1][3]=="1"):
                    Window.checkBox.setChecked(True)
                else:
                    Window.checkBox.setChecked(False)
                    
                if(self.Devices[DeviceSelected][1][4]=="1"):
                    Window.checkBox_2.setChecked(True)
                    Window.checkBox_6.setEnabled(True)
                    Window.groupBox_5.setEnabled(True)
                    Window.label_21.setEnabled(True)
                else:
                    Window.checkBox_2.setChecked(False)
                    Window.groupBox_5.setEnabled(False)
                    Window.checkBox_6.setEnabled(False)
                    Window.label_21.setEnabled(False)
                
                # Set Board Image
                if(self.Devices[DeviceSelected][1][6]=="Original OASIS"):
                    Window.label_2.setPixmap(QtGui.QPixmap(":/Boards/resources/boards/OASISV1.png"))
                elif(self.Devices[DeviceSelected][1][6]=="OASIS-UROS"):
                    Window.label_2.setPixmap(QtGui.QPixmap(":/Boards/resources/boards/OASIS-UROS.png"))
        
                # Enable sampling
                Window.tabWidget.setEnabled(True)
                Window.pushButton_2.setEnabled(True)
                
            else:
                Window.label_2.setPixmap(QtGui.QPixmap(":/Boards/resources/boards/Unknown.png"))
                Window.label_28.setText("Unknown")
                Window.label_8.setText("Unknown")
                Window.label_9.setText("Unknown")
                Window.label_10.setText("Unknown")
                Window.label_11.setText("Unknown")
                Window.checkBox.setChecked(False)
                Window.checkBox_2.setChecked(False)
                
                # Disable sampling
                Window.tabWidget.setEnabled(False)
                Window.pushButton_2.setEnabled(False)
                
        return
    
    def UpdateAllVoltageRanges(self, window):
        
        window.comboBox_2.setCurrentIndex(window.comboBox_11.currentIndex())
        window.comboBox_3.setCurrentIndex(window.comboBox_11.currentIndex())
        window.comboBox_4.setCurrentIndex(window.comboBox_11.currentIndex())
        window.comboBox_5.setCurrentIndex(window.comboBox_11.currentIndex())
        window.comboBox_6.setCurrentIndex(window.comboBox_11.currentIndex())
        window.comboBox_7.setCurrentIndex(window.comboBox_11.currentIndex())
        window.comboBox_8.setCurrentIndex(window.comboBox_11.currentIndex())
        window.comboBox_9.setCurrentIndex(window.comboBox_11.currentIndex())
        
        return