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
		self.fitter = Fitter()

class Wrkr(QtCore.QThread): #või Thread
	#create a dataready signal here but this requires a qobject, right? So QThread it is, still.
	dataReady = QtCore.pyqtSignal(tuple)


	def __init__(self, startsignal, data_queue, settings_queue):
		self.running = Event()
		self.startsignal = startsignal
		self.data_queue = data_queue
		self.settings_queue = settings_queue
		self.numFitters = 2
		self.fitters = [FitContainer()] * self.numFitters



	def stop(self):
		self.running.clear()


	def parseSettings(self):
		#dict format should be like: {'key':[val_1,val_2],...}
		#val = None are ignored
		settings_dict = settings_queue.get(False)
		for key in settings_dict:
			if key in ['active', 'range', 'sloped','cyclic']:
				for i,val in enumerate(settings_dict[key]):
					if val is not None:
						command = "self.fitters[i].{} = val".format(key)
						exec(command)
						#however, if sloped changes, we need to reassign the last function
						#paramlist should be handled fine, though
						#(I don't know about the double ->single transition)
						if key == 'sloped':
							newfunclist = self.fitters[i].fitter.funclist
							newfunclist[-1] = linear if val else lambda x,a : a
							self.fitters[i].fitter.setFuncList(newfunclist)
			if key == 'model':
				for i,val in enumerate(settings_dict[key]):
					if val = 'Double Lorentz':
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
			xData, yData = data_queue.get(False) #get some data
			#siin võib-olla võib neid veel ümber tõsta
			#check param queue & set params
			if not self.settings_queue.empty():
				self.parseSettings()

			# do the fitting(s)
			
			#how we'd like to proceed here? Something like
			for n in range(self.numFitters):
				if self.fitters[n].active:
					#handling of cyclic case should go here

					if (self.fitters[n].fitter.fit(xData[self.fitters[n].range[0]:self.fitters[n].range[1]],
												   yData[self.fitters[n].range[0]:self.fitters[n].range[1]]) == 0):
						#additional evaluation that data is reasonable
						self.dataReady.emit((n, self.fitters[n].fitter.paramlist,
											 xData[self.fitters[n].range[0]:self.fitters[n].range[1]],
											 self.fitters[n].fitter.fitted))
					else:
						self.dataReady.emit((n,None)) # just to signal that fit wasnt successful











		'''
		if self.paramlist is not None and cyclic:  # go cyclic if possible
				delim = (paramlist[0] + paramlist[3]) / 2
			else:
				paramlist = None
				delim = None  # võetakse skaala keskpunkt

			if sloped:
				if paramlist is not None and len(paramlist) == 7:
					paramlist += [0.0]
				fitted, params = fit_DLorentz_slope(np.array(spcData), xData, paramlist, delim)  # eraldusx maksimumide vahel
				paramlist = [params[0][i * 2] for i in range(8)]
			else:
				if paramlist is not None and len(paramlist) == 8:
					paramlist = paramlist[:7]
				fitted, params = fit_DLorentz(np.array(spcData), xData, delim, paramlist)
				paramlist = [params[0][i * 2] for i in range(7)]
			self.success = ??
		return fitted, params
	'''
#kuidas peaksid olema struktureeritud fitifunktsioonid?

