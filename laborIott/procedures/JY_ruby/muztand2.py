#from fittingfns import Lorentz_fit, DLorentz_fit
from fitter import Fitter


class FitContainer(object): # combines Fitter with a few variables relevant to the current case
	def __init__(self):
		self.active = True
		self.range = [0, 1024]
		self.sloped = True
		self.cyclic = True
		self.fitter = Fitter()

class Wrkr(QThread): #või Thread
	#create a dataready signal here but this requires a qobject, right? So QThread it is, still.



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
		pass
		#active
		#range
		#sloped
		#cyclic
		#model

		
	def run(self):
		paramlist = None
		delim = None
		sloped, cyclic = True, True #all of these - handle differently (2 copies needed)
		#well we need a whole set of parameters here
		fitter = [Fitter(DLorentz_fit), Fitter(Lorentz_fit)] #we praably need a different init here

		while(True):
			self.startsignal.emit(True)  # well how can we do it from here?
			# wait for data arrival
			while self.data_queue.empty():
				if not self.running.is_set():
					return
			xData, spcData = data_queue.get(False)
			#check param queue & set params
			if not self.settings_queue.empty():
				sloped, cyclic = settings_queue.get(False)
				#we need to get more data here
				#所以 我們可能有一個 字典 (dictionary)
			# do the fitting(s)
			
			#how we'd like to proceed here? Something like
			for n in range(self.numFitters):
				if fitter_active[n]:
					if (fitter[n].run(xData[begin[n]:end[n]],np.array(spcData[begin[n]:end[n]]), paramlist) == 0):
						#additional evaluation that data is reasonable
						self.dataready.emit((n, params[n],xData[n],fitted[n]))
					else:
						self.dataready.emit((n,None))















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

