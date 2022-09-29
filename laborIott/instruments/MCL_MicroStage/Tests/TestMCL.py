import os
from laborIott.adapters.SDKAdapter import SDKAdapter
from laborIott.instruments.MCL_MicroStage.Inst.MicroStage import MCL_MicroStage


def localPath(filename):
	return os.path.join(os.path.dirname(os.path.abspath(__file__)),filename)

stage = MCL_MicroStage(SDKAdapter(localPath("../Inst/MicroDrive"), False))
#stage.delta = (0, 12.5)
stage.pos = (-0.275,0)
while (stage.ismoving):
    pass
print(stage.pos)