from laborIott.instruments.Inhouse.Mock import Mock
from laborIott.adapters.RNDAdapter import RNDAdapter
from laborIott.adapters.ZMQAdapter import ZMQAdapter

#mock = Mock(RNDAdapter())
mock = Mock(ZMQAdapter("localhost"))
for i in range(10):
	print(mock.rndval)
mock.disconnect()
mock.connect()
for i in range(10):
	print(mock.rndval)
