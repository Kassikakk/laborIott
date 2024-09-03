from laborIott.instruments.instrument import Instrument
from ctypes import create_string_buffer


class Newport1830(Instrument):

	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "Newport1830", **kwargs)
		
		self.interact("newp_usb_init_system()")
		self.interact("newp_usb_init_product(0xCEC7)")
		self.buflen = 128
		self.buf = create_string_buffer(self.buflen) #this length should be enough
		
		#self.interact("newp_usb_get_device_info(%d)" % self.buf)
		
		devinfo = self.interact("newp_usb_get_device_info(byref(c_char*%d))" % self.buflen)[1] #self.buf.value
		devinfo = b"".join(devinfo) #muudame listi bytestringiks
		
		if len(devinfo) > 0: #siis midagi on taga
			#Leiame ID, millega edasisi toiminguid teha
			self.devID = int(devinfo[:devinfo.find(b',')])
		else:
			self.devID = None


	def __del__(self):
		self.interact("newp_usb_uninit_system()")
	
		
	@property
	def power(self):
		if self.devID is not None:
			self.interact("newp_usb_send_ascii(%d, c_char_p(b'D?'), c_ulong(2))" % self.devID)
			pwr = self.interact("newp_usb_get_ascii(%d, byref(c_char*%d), %d, byref(c_ulong))" % (self.devID, self.buflen, self.buflen))[1]
			pwr = b"".join(pwr)
			try:
				return float(pwr[:pwr.find(b'\n')]) #uW
			except ValueError:
				return 0
		else:
			return 0
	
	@property
	def wl(self):
		if self.devID is not None:
			self.interact("newp_usb_send_ascii(%d, c_char_p(b'W?'), c_ulong(2))" % self.devID)
			wlr = self.interact("newp_usb_get_ascii(%d, byref(c_char*%d), %d, byref(c_ulong))" % (self.devID, self.buflen, self.buflen))[1]
			wlr = b"".join(wlr)
			try:
				return int(wlr[:wlr.find(b'\n')])
			except ValueError:
				return 0
		else:
			return 0
			
	@wl.setter
	def wl(self,value):
		if self.devID is not None and value > 200 and value < 1500:
			self.interact("newp_usb_send_ascii(%d, c_char_p(b'W%d'), c_ulong(5))" % (self.devID, value))
			
	@property
	def attenuator(self):
		if self.devID is not None:
			self.interact("newp_usb_send_ascii(%d, c_char_p(b'PM:ATT?'), c_ulong(7))" % self.devID)
			wlr = self.interact("newp_usb_get_ascii(%d, byref(c_char*%d), %d, byref(c_ulong))" % (self.devID, self.buflen, self.buflen))[1]
			wlr = b"".join(wlr)
			try:
				return int(wlr[:wlr.find(b'\n')])
			except ValueError:
				return 0
		else:
			return 0
	
	@attenuator.setter
	def attenuator(self, value):
		if self.devID is not None:
			ivalue = 1 if value else 0
			self.interact("newp_usb_send_ascii(%d, c_char_p(b'PM:ATT %d'), c_ulong(8))" % (self.devID, ivalue))
			
	@property
	def scale(self):
		if self.devID is not None:
			self.interact("newp_usb_send_ascii(%d, c_char_p(b'PM:AUTO?'), c_ulong(8))" % self.devID)
			auto = self.interact("newp_usb_get_ascii(%d, byref(c_char*%d), %d, byref(c_ulong))" % (self.devID, self.buflen, self.buflen))[1]
			auto = b"".join(auto)
			self.interact("newp_usb_send_ascii(%d, c_char_p(b'PM:RANGE?'), c_ulong(9))" % self.devID)
			rng = self.interact("newp_usb_get_ascii(%d, byref(c_char*%d), %d, byref(c_ulong))" % (self.devID, self.buflen, self.buflen))[1]
			rng = b"".join(rng)
			try:
				print(auto)
				return (int(rng[:rng.find(b'\n')]),auto==b"1\n")
			except ValueError:
				return 0
		else:
			return 0

	
	@scale.setter
	def scale(self, value):
		#assume string value -  accepts 'Auto' for now
		if (value == 'Auto'):
			self.interact("newp_usb_send_ascii(%d, c_char_p(b'PM:AUTO 1'), c_ulong(9))" % self.devID)

