from laborIott.adapters.serial import SerialAdapter
from laborIott.instruments.Newport842.Inst.Newport842 import Newport842

pwrmtr = Newport842(SerialAdapter('COM3',baudrate=115200, timeout = 0.3)) #Newport842 powermeter

pwrmtr.wl = 400
for i in range(80):
	print (pwrmtr.power)
	