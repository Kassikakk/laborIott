from laborIott.adapters.ver2.ZMQAdapter import ZMQAdapter
from laborIott.visual import Visual



class VInst(Visual):
	'''
	Base class for visual instruments
	Most of the functions inherit from upper class. What is added:
	-selecting adapter: default or network (specify an .ini file with [ZMQ] section for instruments that need it)
	(and put it in local config/laborIott/Inst, filename <refname>.ini)
	-.ini file location directed to /Inst subfolder
	Each instrument is supposed to have a unique refname which is used for settings file and ZMQ connection id
	Note however that a vinst may have multiple instruments (->refnames).

	'''

	def __init__(self, uifile):
		super().__init__(uifile)
		

	def getConfigSection(self, section, refname):
		refname = "Inst/" + refname
		return super().getConfigSection(section, refname)
		
			

	def getZMQAdapter(self, refname):
		#this will select either the default adapter or ZMQ (possibly some other protocol) if access over LAN is needed
		#so any instrument now should get an adapter through this function
		#the refname argument is because there may be multiple instruments connected to a 
		
		#simple adding seems ok:
		#if any of the following is false, return None
		zmqSection =  self.getConfigSection('ZMQ', refname)
		if zmqSection is None:
			return None
		#no 'active' key or the value is yes
		#print("section found")
		if not zmqSection.getboolean('active', True):
			return None
		#has address
		address = zmqSection.get('address','')
		if len(address) == 0:
			return None
		#print("address ok")
		
		#else construct a ZMQAdapter
		inport = zmqSection.getint('inport',5555)
		outport = zmqSection.getint('outport',inport)
		
		return ZMQAdapter(address, inport) #uus ver





