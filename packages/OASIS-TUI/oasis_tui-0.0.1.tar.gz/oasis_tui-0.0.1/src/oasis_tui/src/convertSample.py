'''
 convertSample.py
 
	Class handling manual conversion of raw sample files

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

import numpy as np

class convertSample():
    def __init__(self):
                
        self.PRECACHE_SIZE = 1000
        
        return
        
    def convertFromMeta(filename, metaContentDict, printLogSignal, DataHandler):
        
        printLogSignal.emit(f"[OASIS-GUI]: Opening measurement defined by '{filename}' ...\n")
        triggered_sample = (float(metaContentDict.get('trigg_level')) !=0)
              
        # Load raw data
        filenameraw = f'{filename[:-4]}raw'
        printLogSignal.emit(f"[OASIS-GUI]: Loading raw sample data from '{filenameraw}' ...\n")
        OASISRawData = open(filenameraw, "rb").read()

        # Load raw pretrigger data
        if triggered_sample:
            filenamerawpretrigg = f'{filename[:-10]}_PRE.OASISraw'
            OASISRawDataPre = open(filenamerawpretrigg, "rb").read()

            # Merge pre trigger data
            OASISRawData = OASISRawDataPre + OASISRawData
        
        # Sort raw sample into ADC bytes and then voltage
        OASISChannelData = np.zeros([int(metaContentDict.get('n_sample')), 8])
        OASISData = np.zeros([8, int(metaContentDict.get('n_sample'))])
        BitDivider = 2**int(metaContentDict.get('ADC_BITS'))/2
        VoltageRange = np.array(metaContentDict.get('VoltageRanges').split(','), dtype = float)
        
        # Seperation of channel bits --------------------------------------------------
        for k in range(0,len(OASISChannelData)):
            for j in range(0,18):
                for n in range(0,8):
                    OASISChannelData[k,n] += (((OASISRawData[k*18+j] & (2**n)) >> n) << (17-j))
                    
            # Convert to Voltage --------------------------------------------------
            for i in range(0,8):
                if OASISChannelData[k,i]/BitDivider <= 1:
                    OASISData[i,k] = (OASISChannelData[k,i]*VoltageRange[i])/BitDivider;
                else:
                    OASISData[i,k] = ((OASISChannelData[k,i]-2*BitDivider)/BitDivider)*VoltageRange[i];
        
        # Assemble time vector --------------------------------------------------
        if triggered_sample:
            N = np.arange((1-1000), int(int(metaContentDict.get('n_sample'))/int(metaContentDict.get('ADC_BITS')))-999, 1)
            t = N/float(metaContentDict.get('f_sample'))
        else:
            t = np.arange(0, float(metaContentDict.get('t_sample')), 1/float(metaContentDict.get('f_sample')))
            
        # Give data to DataHandler
        DataHandler.setData(OASISData, t, filenameraw.split('/')[-1][:-9], triggered_sample)