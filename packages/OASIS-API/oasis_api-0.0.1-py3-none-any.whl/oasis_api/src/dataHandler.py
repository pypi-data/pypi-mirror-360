'''
 dataHandler.py
 
	Class handling plotting and saving of sampled data

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

from scipy.io import savemat
import numpy as np
import matplotlib.pyplot as plt

class dataHandler():
    def __init__(self):
        
        self.OASISData = None
        self.t  = None
        self.fileName = None
        self.triggeredSample = False

        return
    
    def setData(self, OASISData, t, fileName, triggeredSample):
        
        self.OASISData = OASISData
        self.t  = t
        self.fileName = fileName
        self.triggeredSample = triggeredSample
        
        return

    def plotData(self):
        # Data plot --------------------------------------------------
        fig, axs = plt.subplots(2, 4, num=self.fileName)
        j = 0
        axs[0, 0].set_ylabel("Voltage / V")
        axs[1, 0].set_ylabel("Voltage / V")
        for k in range(0,8):
            if k==4:
                j = 1
            fig.set_size_inches(18, 10.5, forward=True)
            axs[j, k-j*4].plot(self.t,self.OASISData[k])
            axs[j, k-j*4].set_title("Channel" + str(k+1))
            axs[j, k-j*4].set_xlabel("Time / s")
            
        if self.triggeredSample:
            axs[0,0].axvline(0,color='black',linestyle='--')
        plt.tight_layout()
        plt.show()

    def saveData(self, Window):
        # Save Data --------------------------------------------------
        saveName = self.fileName + ".mat"

        Window.textEdit.append(f"[OASIS-GUI]: Saving acquired data as {saveName}\n")

        try:
            savemat(saveName, {'OASISChannel': self.OASISData, 'OASISTime': self.t})
            Window.textEdit.append(f"[OASIS-GUI]: {saveName} successfully saved.\n")
        except PermissionError:
            Window.textEdit.append("[OASIS-GUI]: ERROR! Can not write to filesystem. Are you running as admin?\n")
            Window.progressBar_2.setVisible(True)
        
        Window.textEdit.ensureCursorVisible()
        
        return saveName