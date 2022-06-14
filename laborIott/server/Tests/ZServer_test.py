from laborIott.adapters.ZMQAdapter import ZMQAdapter

ad = ZMQAdapter("dummy","localhost",5556,5555)
# same machine you need different ports

#ad.write("control")
#print(ad.read())
print(ad.values("kas siin on mingi"))
print(ad.values("now values"))
ad.write("control")
print(ad.read())