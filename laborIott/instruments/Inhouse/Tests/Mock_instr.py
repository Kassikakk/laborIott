from laborIott.instruments.Inhouse.Mock import Mock
from laborIott.adapters.ver2.RNDAdapter import RNDAdapter
from laborIott.adapters.ver2.ZMQAdapter import ZMQAdapter

#mock = Mock(RNDAdapter())
mock = Mock(ZMQAdapter("localhost"))
for i in range(10):
	print(mock.rndval)
mock.disconnect()
mock.connect()
for i in range(10):
	print(mock.rndval)