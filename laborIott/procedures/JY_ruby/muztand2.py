from fittingfns import Lorentz_fit, DLorentz_fit

class Wrkr(QThread): #või tavathread

	def __init__(self):
		self.running = Event()
		pass
		
	def run(self, data_queue, settings_queue):
		paramlist = None
		delim = None
		sloped, cyclic = True, True
		fitter = [Fitter(DLorentz_fit), Fitter(Lorentz_fit)]
		while(True):
			self.startIdus.emit(True)  # reserve false for abort?
			# wait for data arrival
			while data_queue.empty():
				if not self.running.is_set():
					return
			xData, spcData = data_queue.get(False)
			#check param queue & set params
			if not self.paramQueue.empty():
				sloped, cyclic = settings_queue.get(False)
				#we need to get more data here
			# do the fitting(s)
			
			#how we'd like to proceed here? Something like
			for n in range(2):
				if fitter_active[n]:
					fitted, params = fitter[n].run(np.array(spcData[begin[n]:end[n]]), xData[begin[n]:end[n]], paramlist, delim, sloped)
					if fitter[n].success:
						self.updateData.emit((n,params[0]))
						self.updateFitShape.emit(n, tuple(xData), tuple(fitted[0]), colors[n])



class Fitter(object):
	def __init__(self, func):
		self.paramlist = None #previous values or None if new guessing required
		self.fitfunc = func


		
	def fit(self, data, xdata, cyclic, sloped, delim):
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
	
#kuidas peaksid olema struktureeritud fitifunktsioonid?