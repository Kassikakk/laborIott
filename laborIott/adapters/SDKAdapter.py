

from laborIott.adapters.adapter import Adapter

import platform
import ctypes
import re



class SDKAdapter(Adapter):

	def __init__(self, libname, use_cdll = True):
		super().__init__()
		self.libname = libname
		self.use_cdll = use_cdll


	def connect(self):
		# Check operating system and load library
		# the library should be on PATH or current dir 
		# which is not well defined so PATH it is

		#we delegate the error handling to instrument base class
		#to see if it looks fine
		
		try:
			if platform.system() == "Linux":
				self.conn = ctypes.cdll.LoadLibrary(self.libname) #+'.so'?
			elif platform.system() == "Windows":
				if self.use_cdll:
					self.conn = ctypes.cdll.LoadLibrary(self.libname)
				else:
					self.conn = ctypes.windll.LoadLibrary(self.libname)
			return True
			
		except Exception as e:
			#enact the logging for str(e)
			print(f"conn err {e}")
			self.conn = None 
			return False
			

	def interact(self, command):
		if self.conn is None:
			return None
		#print(command)
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
		exec("a[{}] = self.conn.".format(len(a) - 1) + command)
		#exec('print("a[{}] = self.conn.".format(len(a) - 1) + command)')
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
		return r #maybe [] can be legal here?

	def disconnect(self):
		#This one is tricky. There is generally no "UnloadLibrary" function in ctypes.
		#it is to be seen what works. The following has been suggested, but allegedly
		#can also lead to all kinds of errors; also not sure if it works on all platforms
		#well, it seems to depend on both the platform and the windll/cdll possibly? though not sure

		'''
		def ctypesCloseLibrary(lib):
			dlclose_func = ctypes.WinDLL(None).dlclose
			dlclose_func.argtypes = [ctypes.c_void_p]
			dlclose_func.restype = ctypes.c_int
			dlclose_func(lib._handle)
			'''
		if self.conn is not None:
			#ctypesCloseLibrary(self.conn)
			handle = self.conn._handle
			del self.conn
			ctypes.windll.kernel32.FreeLibrary(handle)
			self.conn = None