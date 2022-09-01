from inspect import signature
import numpy as np

def linear(x, A, B):
        return A + B * x

def Lorentz(x,xc,w,A):
	return A / (w + ((x - xc) ** 2 / w))

fnlist = [Lorentz, Lorentz, linear]
parno = [len(signature(f).parameters) - 1 for f in fnlist]



def fitfn(x, *args):
	result = np.zeros(x.size)
	offset = 0
	for i,f in enumerate(fnlist):
		result += f(x,*args[offset:offset+parno[i]])
		offset += parno[i]
	return result



print(*fitfn(np.arange(-1, 10, 0.1),1,2,3,4,5,6,7,0.1), sep = '\n')
#print(*np.arange(-1, 10, 0.1), sep = '\n')