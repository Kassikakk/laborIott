from Ruby_proc import RubyProc



from laborIott.instruments.MCL_MicroStage.VInst.StageVI import Stage_VI
'''


'''


class RubyStage(RubyProc):

	def __init__(self,uifile, address= None, inport= None, outport = None):):

		self.stage = Stage_VI() #address etc, but eventually this should run from some ini file
		#more inits here
		#mingi signal (or two?) needs to be connected to cycle the positions and return the posindex

		self.stage.show()
		super(RubyStage, self).__init__(uifile, address, inport, outport)
		#ok?


	def update(self, dataTuple):

		super(RubyStage, self).update(dataTuple)

	def saveData(self, name):

		#super(RubyStage, self).saveData(name) #vot siin ma ei tea?