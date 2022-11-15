from turtle import speed
from laborIott.instrument import Instrument

class MCL_MicroStage(Instrument):

	def __init__(self, adapter, **kwargs):
		super().__init__(adapter, "MCL_MicroStage", **kwargs)
		
		self.handle = self.values("MCL_InitHandle()")[0]
		#I keep telling that we need a mechanism for failing connection and later retrial
		#Note that apparently the Linux version uses MCL_MD_xxx prefix, not just MCL_
		#It's not always drop-in (mostly is, though)
		#We'd probably also need some limiting values for coords & speed, so 

		ret = self.values("MCL_MDInformation(byref(c_double), byref(c_double),byref(c_double),\
			byref(c_double),byref(c_double),byref(c_double), %d)" % self.handle)
		#[0, 0.02, 9.525e-05, 4.0, 4.0, 0.0, 0.01905]
		self.encres, self.stepSize, self.maxSpeed, speed2, speed3, self.minSpeed = ret[1:]
		self._speed = self.maxSpeed #bring it to the max
		ret = self.values("MCL_MDReadEncoders(byref(c_double), byref(c_double),byref(c_double),\
			byref(c_double), %d)" % self.handle)


		
	def __del__(self):
		self.write("MCL_ReleaseHandle(%d)" % self.handle)
		
	@property
	def speed(self):
		return self._speed
	
	@speed.setter
	def speed(self, val):
		if val >= self.minSpeed and val <= self.maxSpeed:
			self._speed = val
	

	@property
	def pos(self):
		#make sure we're not moving first
		if (self.ismoving):
			return [None,None]
		ret = self.values("MCL_MDReadEncoders(byref(c_double), byref(c_double),byref(c_double),\
			byref(c_double), %d)" % self.handle)
		return ret[1:3]

	@pos.setter
	def pos(self, val):
		#if is moving, it is possible to 1)disregard, 2)stop 3) wait. Go for 1) for now.
		if self.ismoving:
			return
		if val is None: #use this to reset encoders
			ret = self.values("MCL_MDResetEncoders(byref(c_ushort),%d)" % self.handle)
			return
		curpos = self.pos
		self.delta = (val[0] - curpos[0], val[1] - curpos[1])

	@property
	def ismoving(self):
		ret = self.values("MCL_MicroDriveMoveStatus(byref(c_int), %d)" % self.handle)
		return ret[1]
	
	@ismoving.setter
	def ismoving(self, val):
		if self.ismoving and not bool(val): #only false is accepted
			ret = self.values("MCL_MDStop(byref(c_ushort), %d)" % self.handle)

	@property
	def delta(self):
		return (0,0)
	
	@delta.setter
	def delta(self, val):
		#val is expected to be len 2 list or tuple
		#if one axis is omitted, None can be sent
		if val[0] is None:
			if val[1] is not None:
				self.values("MCL_MDMoveR(1, c_double(%f), c_double(%f), 0, %d)" % (self.speed, val[1], self.handle))
			else:
				return
		elif val[1] is None:
			self.values("MCL_MDMoveR(2, c_double(%f), c_double(%f), 0, %d)" % (self.speed, val[0], self.handle))
		else:
			#print(self.speed, val[0], self.speed, val[1])
			self.values("MCL_MDMoveThreeAxesR(1, c_double(%f), c_double(%f), 0, \
				2, c_double(%f), c_double(%f), 0,\
				3, c_double(0.0), c_double(0.0), 0, %d)" \
				 % (self.speed, val[0], self.speed, val[1], self.handle))
	#x,y
	#speed
	#moving
	#??deltapos, direction, unit
	#as the steps are different, perhaps mm or um is a better