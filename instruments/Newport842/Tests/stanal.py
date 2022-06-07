f = open("sta.txt", "rb")
s = b"\n".join(f.readlines()).decode()
#srch = ("Current Scale", '\t')
#srch = ("Active WaveLength", "nm")
#srch = ("AutoScale", "\r")
#srch = ("Attenuator", "\r")
#srch = ("Max Wavelength index", '\t')
#s = s[s.find(srch[0])+len(srch[0])+2:]
#s = s[:s.find(srch[1])]
print(s)

 
