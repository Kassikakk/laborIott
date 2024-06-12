from laborIott.instruments.Inhouse.Mock import Mock
from laborIott.adapters.ver2.RNDAdapter import RNDAdapter
from laborIott.adapters.ver2.ZMQAdapter import ZMQAdapter

#mock = Mock(RNDAdapter())
mock = Mock(ZMQAdapter("Mock", "localhost",5555,5556))
print(mock.rndval)