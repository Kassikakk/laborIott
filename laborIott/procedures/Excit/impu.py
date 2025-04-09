import importlib as il

#from laborIott.instruments.Newport1830.VInst.Newport1830VI import Newport1830_VI as Newport_VI
m = il.import_module("laborIott.instruments.Newport1830.VInst.Newport1830VI")
mis = "ins"
exec(mis + '= getattr(m,"Newport1830_VI")')
print(ins)