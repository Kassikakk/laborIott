from Ruby_proc import RubyProc
import pandas as pd
import numpy as np
import os, sys
from PyQt5 import QtWidgets

from laborIott.instruments.MCL_MicroStage.VInst.StageVI import Stage_VI

def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)
'''


'''


class RubyStage(RubyProc):

	def __init__(self, uifile, address= None, inport= None, outport = None):

		self.stage = Stage_VI() #address etc, but eventually this should run from some ini file
		#more inits here
		#mingi signal (or two?) needs to be connected to cycle the positions and return the posindex
		#where is the current index held? Here I guess. Hey waida minit, we can access the list of self.stage directly
		#index needs to be here, though
		self.noOfCycles = 10

		self.curPosIndex = 0
		self.data = pd.DataFrame()

		self.stage.show()
		super(RubyStage, self).__init__(uifile, address, inport, outport)
		self.setExternalMode.connect(self.stage.setExternal)
		#ok?


	def update(self, dataTuple):

		self.collecting = True
		#do the main processing
		super(RubyStage, self).update(dataTuple)
		# actually it comes here for every selected fitter, so 0..2 times for every point
		#so we should check here if it is the last one
		if self.fitBox2.isChecked() and dataTuple[0] != 1:
			return
		#well, if neither of the boxes is checked, then...
		


		if len(self.values[dataTuple[0]]) >= self.noOfCycles:
			self.processing.set() #engage waiting event, as this may take some time
			#make sure it doesn't just explode if there are 0 or 1 recorded positions
			keylist = list(self.stage.posDict.keys())

			#save the data and timestamp, data and keystring
			outlist = [self.values[dataTuple[0]][-1][0]] #timestamp
			for i in range(2):
				N = len(self.values[i])
				if N > 0:
					mean = self.colsum[i] / N
					outlist += [mean, np.sqrt(self.colsum2[i] / N  - mean**2)]
				#else [0,0]?
			outlist += keylist[self.curPosIndex]
			self.data = pd.concat([self.data,pd.DataFrame([outlist])])
			#check if name is given
			name = self.nameEdit.text()
			if len(name) > 0:
				self.data.to_csv(os.path.join(self.saveLoc, name), sep='\t', header=False, index=False, float_format="%.4f")

			#move stage to next pos (make sure new scan waits too. We use the processing event for that.)
			noPosItems = len(self.stage.posDict)
			if noPosItems > 0: #1?
				for i in range(3): #3 times is mostly good enough
					self.stage.gotoPos(self.stage.posDict[keylist[self.curPosIndex]], False)
					while self.stage.posReached.is_set(): #jääb siia toppama? timeri handler peaks maha võtma
						pass
				self.curPosIndex += 1
				if self.curPosIndex >= noPosItems:
					self.curPosIndex = 0

			#reset the series
			self.resetSeries()
			self.processing.clear()
			#release waiting event


if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	#app.aboutToQuit.connect(ExitHandler)
	# handle possible command line parameters: address, inport, outport
	args = sys.argv[1:4]
	# port values, if provided, should be integers
	# this errors if they are not
	for i in (1, 2):
		if len(args) > i:
			args[i] = int(args[i])
	window = RubyStage(localPath("RubyPressure.ui"), *args)
	window.show()
	sys.exit(app.exec_())