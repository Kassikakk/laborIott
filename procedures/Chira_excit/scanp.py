
startwl, stepwl, stopwl, powerSeries, spcMeasure, keepShutOpen, pwrTime
signals: setpowerWL, startgotoWL, setIdusShutter, startIdus, setPwrCollection

while np.sign(stepwl)*curwl <= np.sign(stepwl)*stopwl: #enable negative step

			#adjust powermeter wl
			self.emit.setpowerWL(curwl)
				
			#goto wl

			self.emit.startgotoWL(curwl)
			while self.chira.DataQ.empty():
				if breakEvent.isSet():
						return
			#while: wl is sent back from 

			#katsuks alustuseks lihtsama variandi ära teha, kus pole refivõtmist
			#shutter
			if spcMeasure and not keepShutOpen:
				self.emit.setIdusShutter(True)
			
			#start powermeter series
			self.emit.setPwrCollection(True)

			#start acquisition, wait for Idus data or just some time
			if spcMeasure:
				self.emit.startIdus(True) #maybe reserve false for abort?
				#wait for data arrival
				while self.andor.DataQ.empty():
					if breakEvent.isSet():
						return
				spcData = self.andor.DataQ.get(False)
				#aga kuidas siin selle x-skaalaga on?
			else:
				startTime = time()
				while (time() < startTime + pwrTime):
					if breakEvent.isSet():
						return
			
			#stop powermeter series, wait for data
			self.emit.setPwrCollection(False)
			while self.powerm.DataQ.empty():
				if breakEvent.isSet():
						return
			pwrData = self.powerm.DataQ.get(False)

			#close shutters
			if spcMeasure and not keepShutOpen:
				self.emit.setIdusShutter(True)
				
			#order powerdata saving as needed (construct name)
			#order spectral data saving as needed (construct name)
			#calculate and emit (or Queue) results to main thread
			#including progress data
			curwl += stepwl
