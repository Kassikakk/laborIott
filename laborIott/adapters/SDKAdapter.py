import logging

import numpy as np

from laborIott.adapter import Adapter
from collections.abc import Iterable
import platform
import ctypes
import re


class SDKAdapter(Adapter):

	def __init__(self, dllname, use_cdll = True):
		super().__init__()
		# Check operating system and load library
		if platform.system() == "Linux":
			self._dll = ctypes.cdll.LoadLibrary(dllname) #+'.so'?
		elif platform.system() == "Windows":
			if use_cdll:
				self._dll = ctypes.cdll.LoadLibrary(dllname)
			else:
				self._dll = ctypes.windll.LoadLibrary(dllname)

	def write(self, command):
		#just execute
		command = command.replace('c_','ctypes.c_') #tegelikult peaks seda tegema ainult sulgude sees
		#exec("print('self._dll.' + command)")
		exec('self._dll.' + command)


	def values(self, command, **kwargs):
		#execute and return a list of return and byref returned parameters
		#the idea is that if you give it e.g byref(c_float), it will define a
		#variable var = c_float(), call with (..., byref(var),...) and return
		#var.value as a part of the return list. The return value of the function
		#is first in the list.
		#Also, trying to hook array stuff to the scheme: use byref(c_int*len) format
		#to have a list [len] of values returned within the generally returned list
		#but len has to be an int
		'''
		üle kõigi leitud byref-ide:
		-mis on sulgude sisu
		-m = exec('ctypes.'+sisu + '()')
		-a + = [m]
		-asenda sisu 'a[i]'-ga
		retval = exec('dll.'+string)
		lapi retval ja a[i].valued listi (tuplesse) ja tagasta
		'''
		command = command.replace('c_','ctypes.c_')
		#find the (begin, end) of byref clauses
		matches = [match.span() for match in re.finditer('byref\(.*?\)', command)]
		a = []
		#define variables for each byref and construct the command
		for i,m in enumerate(reversed(matches)):
			param = command[m[0]:m[1]]
			varbl = param[param.find('(') + 1:-1] #sulgude sisu
			if  varbl.find('*') == -1: #tavaline muutuja
				exec('a.append(' + varbl + '())')
				#exec('print("a.append(" + varbl + "())")')
				param = 'ctypes.byref(a[{}])'.format(i)
			else: #pointer
				exec('a.append((' + varbl + ')())') #extra ()!
				#exec('print("a.append((" + varbl + ")())")') 
				param = 'a[{}]'.format(i)
			param = 'ctypes.byref(a[{}])'.format(i)
			command = command[:m[0]] + param + command[m[1]:]
		#eeldaks esialgu int returnimist, muude asjadega (nt void) ei tea, mis teeb.
		#võib ju mingi c_xxx.functionName(...) tüüpi süntaksi peale mõelda.
		#veel üks probleem on byref muutujate võimalik algväärtustamine (byref(c_int{3})?)
		a.append(ctypes.c_int())
		exec("a[{}] = self._dll.".format(len(a) - 1) + command)
		#exec('print("a[{}] = self._dll.".format(len(a) - 1) + command)')
		r = []
		for s in reversed(a):
			if type(s) == int:
				r += [s]
			else:
				try:
					iterus = iter(s) #if no exception, iterable
					r += [[k for k in s]] #flip around to "normal" Python values (What in case of float?)
				except TypeError:
					r += [s.value]
		return r

