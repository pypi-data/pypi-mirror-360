'''
 sampleHandler.py
 
	Class handling sample routine with OASIS devices

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
import time
from scipy.io import savemat
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class sampleHandler():
    def __init__(self):
        
        self.OASISData = None
        self.OASISDataRaw = None
        self.t  = None
        
        # Dynamic Acquisition Parameters --------------------------------------------------
        self.Device = None
        self.t_sample = None
        self.f_sample = None
        self.VoltageRange = None
        self.Offset = None
        self.PRECACHE_SIZE = None
        self.sync_mode = None
        
        # Predefined Acquisition Parameters --------------------------------------------------
        self.CACHE_SIZE = 1500

        return
    
    def getAcquisitionParameters(self, Window, Device):
        
        # Acquisition Parameters --------------------------------------------------
        self.Device = Device
        self.serialSpeed = Device[3]
        self.t_sample = float(Window.lineEdit.text())
        self.f_sample = int(Window.lineEdit_2.text())
        self.VoltageRange = np.array([float(Window.comboBox_2.currentText()), float(Window.comboBox_3.currentText()), float(Window.comboBox_4.currentText()), float(Window.comboBox_5.currentText()), float(Window.comboBox_6.currentText()), float(Window.comboBox_7.currentText()), float(Window.comboBox_8.currentText()), float(Window.comboBox_9.currentText())])
        self.triggeredSample = Window.checkBox_3.isChecked()
        self.OversamplingID = Window.comboBox_10.currentIndex()
        self.fileName = Window.LastSampleDevice + "-" + datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
        
        # Device depended parameters--------------------------------------------------
        self.BYTES_PER_SAMPLE = int(int(self.Device[1][2])) # Divide by 2 if 4 channels
        self.BYTES_PER_CACHE = self.BYTES_PER_SAMPLE * self.CACHE_SIZE
        
        # Triggered Sampling --------------------------------------------------
        if self.triggeredSample:
            self.V_TRIGG = float(Window.lineEdit_3.text())
            self.PRECACHE_SIZE = 1000
            self.Offset = 1
            
        else:
            self.V_TRIGG = 0
            self.PRECACHE_SIZE = 0
            self.Offset = 0

        # Sync mode
        if Window.checkBox_6.isChecked():
            if Window.radioButton.isChecked():
                self.sync_mode = 1
            else:
                self.sync_mode = 2
        else:
            self.sync_mode = 0

        # Preallocation
        self.OASISData = np.zeros([8, self.PRECACHE_SIZE + int(self.t_sample*self.f_sample)-self.Offset])

    def SampleSerial(self, printLogSignal, sampleAborted, sampleProgress, DataHandler):
        
        # Open serial connection
        if not self.connectSerial(printLogSignal,sampleAborted):
            self.OASISSerial.close()
            return

        # Set voltage ranges
        self.setVoltageRanges(printLogSignal)
        
        # Set oversampling factor
        self.setOversamplingFactor(printLogSignal)
 
        # Request new sample
        self.requestSample(printLogSignal)
        
        # Get data over serial interface
        if not self.retrieveDataSerial(printLogSignal,sampleAborted,sampleProgress):
            self.OASISSerial.close()
            return
            
        self.OASISSerial.close()
        
        # Convert Samples to voltages
        self.convertSamples(DataHandler)
        
    def resendSampleSerial(self, printLogSignal, sampleAborted, sampleProgress, DataHandler):
        
        # Open serial connection
        if not self.connectSerial(printLogSignal,sampleAborted):
            self.OASISSerial.close()
            return
 
        # Request previous sample
        printLogSignal.emit(f"[OASIS-GUI] Requesting samples for filename '{self.fileName}' again.\n")
        self.requestPreviousSample(printLogSignal)
        
        # Get data over serial interface
        if not self.retrieveDataSerial(printLogSignal,sampleAborted,sampleProgress):
            self.OASISSerial.close()
            return
            
        self.OASISSerial.close()
        
        # Convert Samples to voltages
        self.convertSamples(DataHandler)

    # Serial Connection --------------------------------------------------
    def connectSerial(self, printLogSignal,sampleAborted): 
        try:
            self.OASISSerial = serial.Serial(port=self.Device[0], baudrate=self.serialSpeed, timeout=2)
        except (OSError, serial.SerialException):
            printLogSignal.emit("[OASIS-GUI] DEVICE ERROR! Could not open serial communication.\n")
            printLogSignal.emit("[OASIS-GUI] Data Acquisition aborted.\n")
            sampleAborted.emit()
            return False
        
        while self.OASISSerial.inWaiting():
            SerialAnswer = self.OASISSerial.readline()
            if SerialAnswer !=bytes("","utf-8"):
                if SerialAnswer.startswith(bytes("[OASIS]","utf-8")):
                    printLogSignal.emit(SerialAnswer.decode("utf-8",errors="ignore"))
                else:
                    printLogSignal.emit("[OASIS-GUI] DEVICE ERROR! Unexpected serial communication content.\n")
                    printLogSignal.emit("[OASIS-GUI] Data Acquisition aborted.\n")
                    sampleAborted.emit()
                    return False
        
        return True

    # Set Voltage Ranges --------------------------------------------------    
    def setVoltageRanges(self, printLogSignal): 
        
        VoltageRangeID = np.zeros(8,int)
        
        for k in range(0,8):
            if self.VoltageRange[k]==2.5:
                VoltageRangeID[k] = 1
            elif self.VoltageRange[k]==5:
                VoltageRangeID[k] = 2
            elif self.VoltageRange[k]==6.25:
                VoltageRangeID[k] = 3
            elif self.VoltageRange[k]==10:
                VoltageRangeID[k] = 4
            elif self.VoltageRange[k]==12.5:
                VoltageRangeID[k] = 5
            else:
                raise ValueError("Voltage Range " + str(self.VoltageRange[k]) + " for channel " + str(k+1) + " is invalid.")

        self.OASISSerial.write(bytes("OASIS.SetVoltageRange(" + str(VoltageRangeID[0]) + "," + str(VoltageRangeID[1]) + "," + str(VoltageRangeID[2]) + ","  + 
                str(VoltageRangeID[3]) + "," + str(VoltageRangeID[4]) + "," + str(VoltageRangeID[5]) + "," + str(VoltageRangeID[6]) + ","  + 
                str(VoltageRangeID[7]) + ")","utf-8"))

        then = time.time()
        while True:
            if time.time()-then>2: # Resend command if stuck
                then = time.time()
                self.OASISSerial.write(bytes("OASIS.SetVoltageRange(" + str(VoltageRangeID[0]) + "," + str(VoltageRangeID[1]) + "," + str(VoltageRangeID[2]) + ","  + 
                        str(VoltageRangeID[3]) + "," + str(VoltageRangeID[4]) + "," + str(VoltageRangeID[5]) + "," + str(VoltageRangeID[6]) + ","  + 
                        str(VoltageRangeID[7]) + ")","utf-8"))
            if self.OASISSerial.inWaiting():
                SerialAnswer = self.OASISSerial.readline()
                if SerialAnswer!=bytes("[OASIS] Voltage ranges set.\r\n","utf-8"):
                    if SerialAnswer !=bytes("","utf-8"):
                        printLogSignal.emit(SerialAnswer.decode("utf-8",errors="ignore"))
                else:
                    break
    # Set oversampling factor --------------------------------------------------
    def setOversamplingFactor(self, printLogSignal):
        self.OASISSerial.write(bytes("OASIS.SetOversampling(" + str(self.OversamplingID) + ")","utf-8"))
        
        then = time.time()
        while True:
            if time.time()-then>2: # Resend command if stuck
                then = time.time()
                self.OASISSerial.write(bytes("OASIS.SetOversampling(" + str(self.OversamplingID) + ")","utf-8"))
            if self.OASISSerial.inWaiting():
                SerialAnswer = self.OASISSerial.readline()
                if SerialAnswer!=bytes("[OASIS] Oversampling factor set.\r\n","utf-8"):
                    if SerialAnswer !=bytes("","utf-8"):
                        printLogSignal.emit(SerialAnswer.decode("utf-8",errors="ignore"))
                else:
                    break
    # Write OASIS.Sample() command  --------------------------------------------------
    def requestSample(self, printLogSignal):
        self.OASISSerial.write(bytes("OASIS.Sample(" + str(self.t_sample) + "," + str(self.f_sample) + "," + str(self.V_TRIGG) + "," + str(self.sync_mode) + "," + str(self.fileName) + ")","utf-8"))
        
        then = time.time()
        while True:
            if time.time()-then>2: # Resend command if stuck
                then = time.time()
                self.OASISSerial.write(bytes("OASIS.Sample(" + str(self.t_sample) + "," + str(self.f_sample) + "," + str(self.V_TRIGG) + "," + str(self.sync_mode) + "," + str(self.fileName) + ")","utf-8"))
            if self.OASISSerial.inWaiting():
                SerialAnswer = self.OASISSerial.readline()
                if SerialAnswer!=bytes("[OASIS] Starting sample procedure...\r\n","utf-8"):
                    if SerialAnswer !=bytes("","utf-8"):
                        printLogSignal.emit(SerialAnswer.decode("utf-8",errors="ignore"))
                else:
                    break
                
    # Write OASIS.Sample() command  --------------------------------------------------
    def requestPreviousSample(self, printLogSignal):
        self.OASISSerial.write(bytes("OASIS.SendData(" + str(self.fileName) + ")","utf-8"))
        
        then = time.time()
        while True:
            if time.time()-then>2: # Resend command if stuck
                then = time.time()
                self.OASISSerial.write(bytes("OASIS.SendData(" + str(self.fileName) + ")","utf-8"))
            if self.OASISSerial.inWaiting():
                SerialAnswer = self.OASISSerial.readline()
                if SerialAnswer!=bytes("[OASIS] Sending sample files named " + str(self.fileName) + "...\r\n","utf-8"):
                    if SerialAnswer !=bytes("","utf-8"):
                        printLogSignal.emit(SerialAnswer.decode("utf-8",errors="ignore"))
                else:
                    break
                
    # Retrieve samples via serial interface  --------------------------------------------------
    def retrieveDataSerial(self,printLogSignal,sampleAborted,sampleProgress):
        
        # Variables
        OASISRcvBuffer = np.zeros([int(self.t_sample*self.f_sample) * self.BYTES_PER_SAMPLE - self.Offset*self.BYTES_PER_SAMPLE])
        OASISDataRawMain = np.zeros([int(self.t_sample*self.f_sample) - self.Offset, self.BYTES_PER_SAMPLE])
        OASISDataRawPreTrigg = np.zeros([self.PRECACHE_SIZE, self.BYTES_PER_SAMPLE])
        
        # Wait for incoming data --------------------------------------------------
        while True:
            if self.OASISSerial.inWaiting():
                SerialAnswer = self.OASISSerial.readline()
                if SerialAnswer!=bytes("<>\r\n","utf-8"):
                    if SerialAnswer==bytes("[OASIS] WiFi is ON. Disabling WiFi for Data Acquisition over Serial...\r\n","utf-8"):
                        then = time.time()
                        while time.time()-then<4:
                            pass
                        
                    if SerialAnswer !=bytes("","utf-8"):
                        printLogSignal.emit(SerialAnswer.decode("utf-8",errors="ignore"))
                    if SerialAnswer==bytes("[OASIS] Sampling aborted.\r\n","utf-8") or SerialAnswer==bytes("[OASIS] FATAL ERROR - Sampling too fast! Data processing did not finish in time.\r\n","utf-8"):
                        printLogSignal.emit("[OASIS-GUI] Data Acquisition aborted.\n")
                        sampleAborted.emit()
                        return False
                else:
                    break
        
        dataRcv = 0
        
        # Read buffer and sort in array --------------------------------------------------
        while dataRcv != (int(self.t_sample*self.f_sample/self.CACHE_SIZE)*self.BYTES_PER_CACHE):
            if(self.OASISSerial.inWaiting()):
                _OASISRcvBuffer = self.OASISSerial.read(self.BYTES_PER_CACHE)
                
                if(len(_OASISRcvBuffer)!=self.BYTES_PER_CACHE):
                    printLogSignal.emit("[OASIS-GUI] DEVICE ERROR! Unexpected serial communication timeout.\n")
                    printLogSignal.emit("[OASIS-GUI] Data Acquisition aborted.\n")
                    sampleAborted.emit()
                    return False
                    
                for i, _byte in enumerate(_OASISRcvBuffer):
                    OASISRcvBuffer[i+dataRcv]=_byte
                    tmp = i
            
                dataRcv += tmp + 1
                sampleProgress.emit(int(dataRcv/(int(self.t_sample*self.f_sample/self.CACHE_SIZE)*self.BYTES_PER_CACHE)*100))
                
        _OASISRcvBuffer = self.OASISSerial.read(int(self.t_sample*self.f_sample*self.BYTES_PER_SAMPLE)-int(self.t_sample*self.f_sample/self.CACHE_SIZE)*self.BYTES_PER_CACHE - self.BYTES_PER_SAMPLE*self.Offset)
    
        for i, _byte in enumerate(_OASISRcvBuffer):
            OASISRcvBuffer[i+dataRcv]=_byte

        if(len(OASISRcvBuffer)==(int(self.t_sample*self.f_sample) * self.BYTES_PER_SAMPLE - self.Offset*self.BYTES_PER_SAMPLE)):
            sampleProgress.emit(100)
        else:
            printLogSignal.emit("[OASIS-GUI] DEVICE ERROR! Data has been lost during transmission.\n")
            printLogSignal.emit("[OASIS-GUI] Data Acquisition aborted.\n")
            sampleAborted.emit()
            return False

        
        for i, _byte in enumerate(OASISRcvBuffer):
            OASISDataRawMain[int(i/self.BYTES_PER_SAMPLE),i%self.BYTES_PER_SAMPLE]=_byte
        
        # Convert to Integer --------------------------------------------------
        OASISDataRawMain = OASISDataRawMain.astype(int)
        
        # If Triggered sampling acquire Pre-Trigg Data; assemble everything into one array --------------------------------------------------
        if self.triggeredSample:
        
            # Discard offset sample
            self.OASISSerial.read(self.BYTES_PER_SAMPLE*self.Offset)
            
            # Wait for OASIS to be ready to send pre-trigger data
            time.sleep(0.5)
            
            # Retrieve Pre-Trigger Data
            self.OASISSerial.write(bytes("Drq()","utf-8"))
            
            # Wait for incoming data
            then = time.time()
            while True:
                if time.time()-then>1: # Resend command if stuck
                    then = time.time()
                    self.OASISSerial.write(bytes("Drq()","utf-8"))
                if self.OASISSerial.inWaiting():
                    SerialAnswer = self.OASISSerial.readline()
                    if SerialAnswer!=bytes("<>\r\n","utf-8"):
                        if SerialAnswer !=bytes("","utf-8"):
                            printLogSignal.emit(SerialAnswer.decode("utf-8",errors="ignore"))
                    else:
                        break

            # Read buffer and sort in array
            _OASISDataRawPreTrigg = self.OASISSerial.read(self.BYTES_PER_SAMPLE*self.PRECACHE_SIZE)
            
            for i, _byte in enumerate(_OASISDataRawPreTrigg):
                OASISDataRawPreTrigg[int(i/self.BYTES_PER_SAMPLE),i%self.BYTES_PER_SAMPLE]=_byte
                
            # Convert to Integer
            OASISDataRawPreTrigg = OASISDataRawPreTrigg.astype(int)
            
            self.OASISDataRaw = np.concatenate((OASISDataRawPreTrigg,OASISDataRawMain))
            
        else:
            self.OASISDataRaw = OASISDataRawMain
            
        printLogSignal.emit("[OASIS-GUI] Data Acquisition finished.\n\n")
        
        return True
    
    # Convert bytes to voltages  --------------------------------------------------
    def convertSamples(self,DataHandler):
        
        # Variables --------------------------------------------------
        OASISChannelData = np.zeros([self.PRECACHE_SIZE + int(self.t_sample*self.f_sample) - self.Offset, 8])
        
        # Seperation of channel bits --------------------------------------------------
        if(self.BYTES_PER_SAMPLE==18):
            for k in range(0,len(self.OASISDataRaw)):
                OASISChannelData[k,0] = (self.OASISDataRaw[k,0] << 10) + (self.OASISDataRaw[k,1] << 2) + (self.OASISDataRaw[k,2] >> 6)
                OASISChannelData[k,1] = ((self.OASISDataRaw[k,2]-((self.OASISDataRaw[k,2] >> 6) << 6)) << 12) + (self.OASISDataRaw[k,3] << 4) + (self.OASISDataRaw[k,4] >> 4)
                OASISChannelData[k,2] = ((self.OASISDataRaw[k,4]-((self.OASISDataRaw[k,4] >> 4) << 4)) << 14) + (self.OASISDataRaw[k,5] << 6) + (self.OASISDataRaw[k,6] >> 2)
                OASISChannelData[k,3] = ((self.OASISDataRaw[k,6]-((self.OASISDataRaw[k,6] >> 2) << 2)) << 16) + (self.OASISDataRaw[k,7] << 8) + (self.OASISDataRaw[k,8])
                OASISChannelData[k,4] = (self.OASISDataRaw[k,9] << 10) + (self.OASISDataRaw[k,10] << 2) + (self.OASISDataRaw[k,11] >> 6)
                OASISChannelData[k,5] = ((self.OASISDataRaw[k,11]-((self.OASISDataRaw[k,11] >> 6) << 6)) << 12) + (self.OASISDataRaw[k,12] << 4) + (self.OASISDataRaw[k,13] >> 4)
                OASISChannelData[k,6] = ((self.OASISDataRaw[k,13]-((self.OASISDataRaw[k,13] >> 4) << 4)) << 14) + (self.OASISDataRaw[k,14] << 6) + (self.OASISDataRaw[k,15] >> 2)
                OASISChannelData[k,7] = ((self.OASISDataRaw[k,15]-((self.OASISDataRaw[k,15] >> 2) << 2)) << 16) + (self.OASISDataRaw[k,16] << 8) + (self.OASISDataRaw[k,17])
                
        elif(self.BYTES_PER_SAMPLE==8):
            for k in range(0,len(self.OASISDataRaw)):
                OASISChannelData[k,0] = (self.OASISDataRaw[k,0] << 8) + (self.OASISDataRaw[k,1])
                OASISChannelData[k,1] = (self.OASISDataRaw[k,2] << 8) + (self.OASISDataRaw[k,3])
                OASISChannelData[k,2] = (self.OASISDataRaw[k,4] << 8) + (self.OASISDataRaw[k,5])
                OASISChannelData[k,3] = (self.OASISDataRaw[k,6] << 8) + (self.OASISDataRaw[k,7])
                
        # Convert to Voltage --------------------------------------------------
        BitDivider = 2**int(self.Device[1][2])/2
        
        for k in range(0,len(self.OASISDataRaw)):
            for i in range(0,8):
                if OASISChannelData[k,i]/BitDivider <= 1:
                    self.OASISData[i,k] = (OASISChannelData[k,i]*self.VoltageRange[i])/BitDivider;
                else:
                    self.OASISData[i,k] = ((OASISChannelData[k,i]-2*BitDivider)/BitDivider)*self.VoltageRange[i];
        
        # Assemble time vector --------------------------------------------------
        if self.triggeredSample:
            N = np.arange((1-self.PRECACHE_SIZE), self.t_sample*self.f_sample, 1)
            self.t = N/self.f_sample
        else:
            self.t = np.arange(0, self.t_sample, 1/self.f_sample)
            
        # Give data to DataHandler
        DataHandler.setData(self.OASISData, self.t, self.fileName, self.triggeredSample)