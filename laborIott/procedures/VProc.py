
from laborIott.visual import Visual



class VProc(Visual):

	'''
	Base class for visual procedure windows
	'''

	def __init__(self, uifile):
		super().__init__(uifile)

	
	def getConfigSection(self, section, refname):
		refname = "Proc/" + refname
		return super().getConfigSection(section, refname)