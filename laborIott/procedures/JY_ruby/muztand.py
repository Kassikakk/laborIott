	def runProc(self):
		while(True):
			#get andor spectral data
			self.startIdus.emit(True)
			# wait for data arrival
			while self.andor.dataQ.empty():
				if not self.running.is_set():
					return
			#set an event here
			self.processing.set()
			self.updateData.emit(self.andor.dataQ.get(False))
			#now wait until the event is cleared 
			while self.processing.is_set():
				if not self.running.is_set():
					self.processing.clear() #make sure it is cleared
					return


	def update(self, spcData):
		#get andor x data
		xData = self.andor.xarr
		
		if self.paramlist is not None and self.cyclicCheck.isChecked():  # go cyclic if possible
			delim = (self.paramlist[0] + self.paramlist[3]) / 2
		else:
			self.paramlist = None
			delim = None  # võetakse skaala keskpunkt
		
		if self.slopeCheck.isChecked():
			if self.paramlist is not None and len(self.paramlist) == 7:
				self.paramlist += [0.0]
			fitted, params = fit_DLorentz_slope(np.array(spcData), xData, delim,
												self.paramlist)  # eraldusx maksimumide vahel
			self.paramlist = [params[0][i * 2] for i in range(8)]
		else:
			if self.paramlist is not None and len(self.paramlist) == 8:
				self.paramlist = self.paramlist[:7]
			fitted, params = fit_DLorentz(np.array(spcData), xData, delim, self.paramlist)
			self.paramlist = [params[0][i * 2] for i in range(7)]
		self.updateFitShape.emit(0, tuple(xData), tuple(fitted[0]), 'w')
		
		p = (params[6] - float(self.zeroValEdit.text()))/float(self.coefEdit.text())
		#self.pLabel.setText("{:.2f}".format(p))
		self.pLabel.setText("{:.2f}".format(params[6]))
		self.RLabel.setText("{:.4f}".format(params[7]))
		self.SNLabel.setText("{:.1f}".format(params[-1]))
		self.processing.clear()
