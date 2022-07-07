	def runProc(self):
		spcData = None
		while(True):
			#get andor spectral data
			self.startIdus.emit(True)
			#process previous data while acquiring
			if spcData is not None:
				self.updateData.emit(spcData)
			# wait for data arrival
			while self.andor.dataQ.empty():
				if not self.running.is_set():
					return
			spcData = self.andor.dataQ.get(False)
			#check once more
			if not self.running.is_set():
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
