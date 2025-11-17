Dx = 2
Dy = 2
step =  0.2
Nx = int(Dx / step)
Ny = int(Dy / step)
for y in range(Ny):
	for x in range(Nx):
		print("{}	{}".format(x*step, y*step))