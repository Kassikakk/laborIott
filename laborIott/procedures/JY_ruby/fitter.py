from inspect import signature
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import t as tdist
from math import sqrt

class Fitter(object):

	def __init__(self, funclist):
		self.paramlist = []
		self.funclist = []
		self.uncertlist = []
		self.fitted = np.array([])
		self.parno = []
		self.chi = 0.0
		if hasattr(funclist, '__iter__' ):
			self.setFuncList(funclist)

	def setFuncList(self, funclist):
		self.funclist = funclist
		self.parno = [len(signature(f).parameters) - 1 for f in funclist]
		# also correct paramlist length
		new_parcount = sum(self.parno)
		old_parcount = len(self.paramlist)
		if old_parcount > new_parcount: #truncate from right
			self.paramlist = self.paramlist[:new_parcount]
		elif old_parcount < new_parcount: # pad to the right and init with zeroes
			print(type(self.paramlist))
			print(new_parcount - old_parcount)
			while len(self.paramlist) < new_parcount:
				self.paramlist.append(0.0)
			print(self.paramlist)

	def fitfn(self, x, *args):
		result = np.zeros(x.size)
		offset = 0
		for i, f in enumerate(self.funclist):
			result += f(x, *args[offset:offset + self.parno[i]])
			offset += self.parno[i]
		return result


	def fit(self, xdata, ydata):

		try:
			#ffnn = lambda x, *args : self.fitfn(x, *args)
			popt, pcov = curve_fit(self.fitfn, xdata, ydata, self.paramlist)
		except RuntimeError:  # siis järelikult ei taha koonduda
			return 1
		#if successful so far, we'd like to evaluate the meaningfulness of the outcome further
		#first see what the covariance matrix looks like

		try:
			#errcoef = 1 #this should be the Student coefficient, see it later
			
			
			df = len(xdata) - len(self.paramlist) #vabadusastmete arv (äkki veel -1 ka?)
			#if errcoef is None: #Studenti koefitsient vastavalt  etteantud konfidentsile:
			conflevel = 0.99
			errcoef = tdist.interval(conflevel, df, loc=0, scale=1)[1]
			
			self.uncertlist = [errcoef * sqrt(pcov[n, n]) for n in range(len(popt))]
		except TypeError:  # mingil juhul seal pcov = inf ja käitub floadina
			return 2
		except ValueError:
			return 3
		#now let's calculate the fitted shape:
		self.fitted = self.fitfn(xdata, *popt)
		self.chi = sqrt(sum((ydata - self.fitted)**2)/len(xdata))
		#we can now probably draw some conclusions based on the chi value
		#and if ok, evaluate the paramlist
		self.paramlist = list(popt)
		return 0
