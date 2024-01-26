from laborIott.adapters.adapter import Adapter
import usb.core
from threading import Lock, Event

class USBAdapter(Adapter):
	""" Adapter class for using the direct USB connection (like V-USB)
	via control transfers
	"""

	def __init__(self, vid, pid, **kwargs):
		super().__init__()
		self.vid = vid
		self.pid = pid
		self.usblock = Lock()
		self.connBusy = Event()
		self.connBusy.set()
		#in principle, other ways (productname ... ) could be figured, too

	def connect(self):
		self.conn = usb.core.find(idVendor = self.vid, idProduct = self.pid) 
		print(self.conn)
		return self.conn is not None
	


	def interact(self, command):

		#command could be a list of [index, value] here?
		#Then one could just
		#self.usblock.acquire(True)
		self.connBusy.wait()
		self.connBusy.clear()
		#try for usb.core.USBError 
		ret = self.conn.ctrl_transfer(0xc0, *command )#bReq, wVal, wIndex, len)
		self.connBusy.set()
		#self.usblock.release()
		return ret
		#well, ok maybe it gets a bit more complex, but not much 
		#-when should one use 0x40?
		#-it already returns a list, but it might need some rearrangement

	def disconnect(self):
		if self.conn is None:
			return
		#self.conn.close() #i don't think it exists. We may need to try what works
