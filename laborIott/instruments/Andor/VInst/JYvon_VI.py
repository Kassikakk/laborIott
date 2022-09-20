from laborIott.instruments.Andor.VInst.AndorVI import Andor_VI
from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
from laborIott.instruments.Andor.VInst.LambdaDlg import Ui_LambdaDialog  # pyuic5 generated dialog
import os, sys


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


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
		self.dlg.closeEvent = self.removeLines

		self.lambdaButt.setEnabled(True)
		# any additional disablements?

		self.neSpins = [self.lamDlg.NeSpin1,self.lamDlg.NeSpin2,self.lamDlg.NeSpin3]
		self.neVals = [692.94675, 693.7664, 696.5431]
		self.neChecks = [self.lamDlg.NeCheck1,self.lamDlg.NeCheck2,self.lamDlg.NeCheck3]
		self.necolors = ['r','g','b']
		self.nelns = []
		# we'll try to make them appear and disappear with the dialog?
		for i in range(3):
			self.nelns += [pg.InfiniteLine(self.xarr[self.neSpins[i].value()])]
			self.graphicsView.addItem(self.nelns[i])
			self.nelns[i].setPen(None)
		#self.onCalcLambda()
		self.onCalcFromLimb(6256.0)
		self.lambdaButt.clicked.connect(self.setLambdaDlg)
		for i in range(3):
			self.neSpins[i].valueChanged.connect(lambda x, a=i: self.nelns[a].setPos(self.xarr[x]))
			self.neChecks[i].clicked.connect(
				lambda x, a=i: self.nelns[a].setPen(self.necolors[a] if self.neChecks[a].isChecked() else None))

		self.lamDlg.calcLmbdButt.clicked.connect(self.onCalcLambda)

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
		self.xarr = np.array([(limbval - (bn + bp * (512.0 - p)))/(an + ap * (512.0 - p)) for p in range(1024)])
		#ok but we should also adjust the Ne line markers here
		step = (self.xarr[1023] - self.xarr[0]) / 1023
		self.lamDlg.startEdit.setText("{:.5f}".format(self.xarr[0]))
		self.lamDlg.stepEdit.setText("{:.5f}".format(step))

		for i in range(3):
			pos = int((self.neVals[i] -self.xarr[0]) / step )
			if (pos > -1) and (pos < 1024):
				self.neSpins[i].setValue(pos)
				self.nelns[i].setPos(self.xarr[self.neSpins[i].value()])


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
			self.xarr = np.arange(len(self.xarr)) * step + start  # we could also separate this action
			self.lamDlg.startEdit.setText("{:.5f}".format(start))
			self.lamDlg.stepEdit.setText("{:.5f}".format(step))
			# readjust line positions
			for i in range(3):
				self.nelns[i].setPos(self.xarr[self.neSpins[i].value()])

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
