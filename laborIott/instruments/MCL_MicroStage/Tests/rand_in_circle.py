from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.MCL_MicroStage.MicroStage import MCL_MicroStage
from math import pi, cos, sin
from random import uniform

stage = MCL_MicroStage(SDKAdapter("MicroDrive", False))
x0 = -0.1
y0 = 7
R = 2.7

while(True):
	#get the r value
	r = uniform(0,R)
	phi = uniform(0,2*pi)
	x = x0 + r * cos(phi)
	y = y0 + r * sin(phi)
	#print(x,y)
	stage.pos = [x,y]
	while (stage.ismoving):
		pass
	
