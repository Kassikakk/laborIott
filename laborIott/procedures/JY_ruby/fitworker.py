#from fittingfns import Lorentz_fit, DLorentz_fit
from fitter import Fitter
from PyQt5 import QtCore
from threading import Event
import numpy as np

def linear(x, A, B):
	return A + B * x

def Lorentz(x,xc,w,A):
	return A / (w + ((x - xc) ** 2 / w))

def Gauss(x,xc,w,A):
	return A * np.exp(-((x - xc) / (2*w))** 2)


class FitContainer(object): # combines Fitter with a few variables relevant to the current case
	def __init__(self):
		self.active = True
		self.range = [0, 1024]
		self.sloped = True
		self.cyclic = True
		self.relrange = False
		self.fitter = Fitter([])

class FitWorker(QtCore.QThread): #või Thread
	#create a dataready signal here but this requires a qobject, right? So QThread it is, still.
	dataReady = QtCore.pyqtSignal(tuple)


	def __init__(self, startsignal, data_queue, settings_queue):
		super(FitWorker, self).__init__()
		self.running = Event()
		self.startsignal = startsignal
		self.data_queue = data_queue
		self.settings_queue = settings_queue
		self.numFitters = 2
		self.fitters = []
		for i in range(self.numFitters):
			self.fitters += [FitContainer()] 
		



	def stop(self):
		self.running.clear()


	def parseSettings(self):
		#dict format should be like: {'key':[val_1,val_2],...}
		#val = None are ignored
		settings_dict = self.settings_queue.get(False)
		for key in settings_dict:
			if key in ['active', 'range', 'sloped','cyclic', 'relrange']:
				for i,val in enumerate(settings_dict[key]):
					if val is not None:
						command = "self.fitters[i].{} = val".format(key)
						exec(command)
						#exec("print(self.fitters[i].{}, i, val)".format(key))
						#however, if sloped changes, we need to reassign the last function
						#paramlist should be handled fine, though
						#(I don't know about the double ->single transition)
						if key == 'sloped':
							newfunclist = self.fitters[i].fitter.funclist
							if len(newfunclist) > 0:
								newfunclist[-1] = linear if val else lambda x,a : a
								self.fitters[i].fitter.setFuncList(newfunclist)
			if key == 'model':
				for i,val in enumerate(settings_dict[key]):
					if val == 'Double Lorentz':
						self.fitters[i].fitter.setFuncList([Lorentz, Lorentz, linear if self.fitters[i].sloped else lambda x,a : a])
						plist = self.fitters[i].fitter.paramlist
						plist[0] = 695
						plist[3] = 693
						plist[1] = plist[4] = 1

					elif val == 'Single Lorentz':
						self.fitters[i].fitter.setFuncList(
							[Lorentz, linear if self.fitters[i].sloped else lambda x, a: a])
						plist = self.fitters[i].fitter.paramlist
						plist[0] = 695
						plist[1] = 1
						plist[-1] = 0 #I think this is needed if we reduce from double
					elif val == 'Single Gauss':
						self.fitters[i].fitter.setFuncList(
							[Gauss, linear if self.fitters[i].sloped else lambda x, a: a])
						plist = self.fitters[i].fitter.paramlist
						plist[0] = 695
						plist[1] = 1
						plist[-1] = 0


		
	def run(self):
		self.running.set()

		while(True):
			self.startsignal.emit(True)  # hope it wööks?
			# wait for data arrival
			while self.data_queue.empty():
				if not self.running.is_set():
					return
			xData, yData = self.data_queue.get(False) #get some data


			#siin võib-olla võib neid veel ümber tõsta
			#check param queue & set params
			if not self.settings_queue.empty():
				self.parseSettings()

			# do the fitting(s)
			
			#how we'd like to proceed here? Something like
			for n in range(self.numFitters):
				if self.fitters[n].active:
					#handling of cyclic case should go here
					if not self.fitters[n].cyclic:
						#print(self.fitters[n].fitter.paramlist)
						plist = self.fitters[n].fitter.paramlist #plist is just a reference here
						for i in range(len(plist)):
							plist[i] = 0
						plist[0] = xData[max(enumerate(yData), key = lambda y: y[1])[0]] #was 695
						plist[1] = 1
						if len(plist) > 6:  #well if there are more parameters (like Voigt...)?
							plist[3] = plist[0] - 2 #this is somewhat arbitrary
							plist[4] = 1
						#print(self.fitters[n].fitter.paramlist)
					#clarify the range here. If it is relative or absolute.
					#for absolute, it's easy. For relative we take plist[0] and find the point
					#then develop from there
					if self.fitters[n].relrange:
						#I think we can use this trick to get the x-value index:
						xi = min(enumerate(xData), key = lambda x: abs(self.fitters[n].fitter.paramlist[0] - x[1]))[0]
						p1 = xi - abs(self.fitters[n].range[0])
						p2 = xi + abs(self.fitters[n].range[1])
					else:
						p1 = abs(self.fitters[n].range[0])
						p2 = abs(self.fitters[n].range[1])
					#check if we're still within range
					p1 = 0 if p1 < 0 else p1
					p2 = 1024 if p2 > 1024 else p2




					if (self.fitters[n].fitter.fit(xData[p1:p2], yData[p1:p2]) == 0):
						#additional evaluation that data is reasonable
						self.dataReady.emit((n, self.fitters[n].fitter.paramlist,
											 xData[p1:p2], self.fitters[n].fitter.fitted, 
											 self.fitters[n].fitter.uncertlist, 
											 self.fitters[n].fitter.rsqr))
						#print(n,self.fitters[n].range[0],self.fitters[n].range[1])
						#also send other evaluative data. Uncertainty approximation and goodness of fit
					else:
						#print("unsuccess")
						self.dataReady.emit((n,None)) # just to signal that fit wasnt successful

