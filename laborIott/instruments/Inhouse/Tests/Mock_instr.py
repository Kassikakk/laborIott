from laborIott.instruments.Inhouse.Mock import Mock
from laborIott.adapters.ver2.RNDAdapter import RNDAdapter

mock = Mock(RNDAdapter())
print(mock.rndval[0])