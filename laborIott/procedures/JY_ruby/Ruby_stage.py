from Ruby_proc import RubyProc



from laborIott.instruments.MCL_MicroStage.VInst.StageVI import Stage_VI
'''


'''


class RubyStage(RubyProc):

	def __init__(self,uifile, address= None, inport= None, outport = None):):

		self.stage = Stage_VI() #address etc, but eventually this should run from some ini file
		#more inits here
		#mingi signal (or two?) needs to be connected to cycle the positions and return the posindex
		#where is the current index held? Here I guess. Hey waida minit, we can access the list of self.stage directly
		#index needs to be here, though
		self.noOfCycles = 30

		self.curPosIndex = 0

		self.stage.show()
		super(RubyStage, self).__init__(uifile, address, inport, outport)
		#ok?


	def update(self, dataTuple):
		#this will catch every fitting, right?
		#so we count a number of calls here
		#then move the stage and write the data
		#also waiting for the stagemove to happen
		self.collecting = True

		if len(self.values) >= self.noOfCycles:
			#save the data and timestamp

			#move stage to next pos (make sure new scan waits too? Dowe need an extra event for that?)
			noPosItems = len(self.stage.posDict)
			if noPosItems > 0: #1?
				self.stage.posDict[self.curPosIndex]
			#reset the series
			self.resetSeries()

		super(RubyStage, self).update(dataTuple)

	def saveData(self, name):

		#super(RubyStage, self).saveData(name) #vot siin ma ei tea?

if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	app.aboutToQuit.connect(ExitHandler)
	# handle possible command line parameters: address, inport, outport
	args = sys.argv[1:4]
	# port values, if provided, should be integers
	# this errors if they are not
	for i in (1, 2):
		if len(args) > i:
			args[i] = int(args[i])
	window = RubyStage("RubyPressure.ui", *args)
	window.show()
	sys.exit(app.exec_())