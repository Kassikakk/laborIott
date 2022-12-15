from laborIott.instruments.Andor.VInst.AndorVI import Andor_VI
from laborIott.utils.fitter import Fitter
from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
from laborIott.instruments.Andor.VInst.LambdaDlg import Ui_LambdaDialog  # pyuic5 generated dialog
import os, sys


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

#Gauss function for line fitting
def Gauss(x,xc,w,A):
	return A * np.exp(-((x - xc) / (2*w))** 2)


class JYvon_VI(Andor_VI):
	'''
	Implements an additional wavelength correction functionality via 3 Ne / Ar lines
	To be merged with Andor_VI in the future with a more flexible lambda correction utility
	usable with a wider range of spectrometers.
	'''

	def __init__(self, address= None, inport= None, outport = None):
		super(JYvon_VI, self).__init__(address, inport, outport)
		self.dlg = QtWidgets.QDialog()
		self.lamDlg = Ui_LambdaDialog()
		self.lamDlg.setupUi(self.dlg)
		self.keepNeLines = True
		if not self.keepNeLines:
			self.dlg.closeEvent = self.removeLines

		self.lambdaButt.setEnabled(True)
		# any additional disablements?

		self.neSpins = [self.lamDlg.NeEdit1,self.lamDlg.NeEdit2,self.lamDlg.NeEdit3]
		self.neVals = [692.94675, 693.7664, 696.5431]
		self.neChecks = [self.lamDlg.NeCheck1,self.lamDlg.NeCheck2,self.lamDlg.NeCheck3]
		self.necolors = ['r','g','b']
		self.nelns = []
		# we'll try to make them appear and disappear with the dialog?
		for i in range(3):
			self.nelns += [pg.InfiniteLine(self.xdata[self.neSpins[i].value()])]
			self.graphicsView.addItem(self.nelns[i])
			if not self.keepNeLines:
				self.nelns[i].setPen(None)
		#self.onCalcLambda()
		self.onCalcFromLimb(6259.0)
		self.lambdaButt.clicked.connect(self.setLambdaDlg)
		for i in range(3):
			self.neSpins[i].valueChanged.connect(lambda x, a=i: self.nelns[a].setPos(self.xdata[x]))
			self.neChecks[i].clicked.connect(
				lambda x, a=i: self.nelns[a].setPen(self.necolors[a] if self.neChecks[a].isChecked() else None))

		self.lamDlg.calcLmbdButt.clicked.connect(self.onCalcLambda)
		self.lamDlg.fitPxelButt.clicked.connect(self.fitNeLines)

		#create some overlays
		self.noOverlays = 3
		self.overlays = []
		for i in range(self.noOverlays):
			self.overlays += [self.graphicsView.plot(pen = None)]
			#self.graphicsView.addItem(self.overlays[i])
			#self.overlays[i].setPen(None)


	def onCalcFromLimb(self, limbval):
		#set xarr from limb value
		#use the approximations made previously, see Dyelaser excitation
		#we should also check here that limbval is float(able)
		an = 9.002
		bn = 13.45
		ap = -6.26E-5
		bp = 0.108
		self.xdata = np.array([(limbval - (bn + bp * (512.0 - p)))/(an + ap * (512.0 - p)) for p in range(1024)])
		#ok but we should also adjust the Ne line markers here
		step = (self.xdata[1023] - self.xdata[0]) / 1023
		self.lamDlg.startEdit.setText("{:.5f}".format(self.xdata[0]))
		self.lamDlg.stepEdit.setText("{:.5f}".format(step))

		for i in range(3):
			pos = int((self.neVals[i] -self.xdata[0]) / step )
			if (pos > -1) and (pos < 1024):
				self.neSpins[i].setValue(pos)
				self.nelns[i].setPos(self.xdata[self.neSpins[i].value()])

	def fitNeLines(self):
		#define fitter 
		fitter = Fitter([Gauss, lambda x, a: a])
		# ± how many points is searched from spinner or fitted from maximum 
		srchrange = 20
		fitrange = 15
		#Go over all lines
		for i in range(3):
			if not self.neChecks[i].isChecked():
				continue
			#set the search range; keep it within limits
			try:
				n1 = n2 =  int(float(self.neSpins[i].getText()))
			except ValueError:
				continue
			n1 -= srchrange
			if n1 < 0: n1 = 0
			n2 += srchrange
			if n2 > (len(self.ydata) - 1): n2 = len(self.ydata) - 1 
			#search the maximum within [n1:n2], record pixel index and max value
			nmax = max(enumerate(self.ydata[n1:n2]), key = lambda x: x[1])[0]
			ymax = self.ydata[nmax]
			y0 = min(self.ydata[n1:n2])
			#now redefine n1, n2 to fitting range
			n1 = nmax  - fitrange
			if n1 < 0: n1 = 0
			n2 = nmax + fitrange
			if n2 > (len(self.ydata) - 1): n2 = len(self.ydata) - 1
			#configure the fitter and do the fitting
			fitter.paramlist = [float(nmax), 1.0, ymax, y0]
			if (fitter.fit(list(range(n1, n2)), self.ydata[n1:n2]) == 0):
				#fitting results are in
				self.neSpins[i].setText("{:.3f}".format(fitter.paramlist[0]))
				print(fitter.paramlist) #diagnostically
				#move the line to place (maybe they will go if change acts programmatically)
				#also record fitter.uncertlist[0]
				#and if wanted, show self.xdata[n1:n2], fitter.fitted in an overlay
				#wait a little maybe
	#you can clear the overlay here


	def onCalcLambda(self):
		points = []
		vals = []
		for i in range(3):
			if self.neChecks[i].isChecked():
				points += [self.neSpins[i].value()]
				vals += [self.neVals[i]]
		N = len(points)
		if N == 0:
			return
		elif N == 1:
			pass  # figure out something here
		else:
			Ex = sum(points)
			Ey = sum(vals)
			Exx = sum([a * a for a in points])
			Eyy = sum([a * a for a in vals])
			Exy = sum([points[a] * vals[a] for a in range(N)])
			Sxx = Exx - Ex * Ex / N
			Syy = Eyy - Ey * Ey / N
			Sxy = Exy - Ex * Ey / N
			step = Sxy / Sxx
			start = (Ey - step * Ex) / N + step
			# r=Sxy/sqrt(fabs(Sxx*Syy))
			self.xdata = np.arange(len(self.xdata)) * step + start  # we could also separate this action
			self.lamDlg.startEdit.setText("{:.5f}".format(start))
			self.lamDlg.stepEdit.setText("{:.5f}".format(step))
			# readjust line positions
			for i in range(3):
				self.nelns[i].setPos(self.xdata[self.neSpins[i].value()])

	def setLambdaDlg(self):
		self.dlg.show()
		for i in range(3):
			self.nelns[i].setPen(self.necolors[i] if self.neChecks[i].isChecked() else None)
		
	
	def removeLines(self, event):
		for i in range(3):
			self.nelns[i].setPen(None)

	def setOverlay(self, index, x, y, color):
		if index > self.noOverlays or index < 0:
			return
		self.overlays[index].setData(x,y)
		self.overlays[index].setPen(color)




if __name__ == '__main__':
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance()
	
	# handle possible command line parameters: address, inport, outport
	args = sys.argv[1:4]
	# port values, if provided, should be integers
	# this errors if they are not
	for i in (1,2):
		if len(args) > i:
			args[i] = int(args[i])

	window = JYvon_VI(*args)
	window.show()
	sys.exit(app.exec_())
