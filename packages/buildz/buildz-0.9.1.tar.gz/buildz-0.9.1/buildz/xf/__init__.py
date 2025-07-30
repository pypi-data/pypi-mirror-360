

#print("xf.__init__")
from .readz import loads, load, loadf, loads_args, loadx, is_args, loadxf
from .writez import dumps, dump, dumpf, dumpx, dumpxf
from .file import *
from .mapz import *
from .xargs import fetch as args

try:
    # C++加速代码
    #from .cpp import pcxf
    #print(f"pcxf:", pcxf)
    #print(f"pcxf.loads:", dir(pcxf))
    from buildz.xf.cpp.pcxf import loads, loadx
    loads_args = loadx
except Exception as exp:
    #print("init not cpp:",exp)
    pass
pass
__author__ = "Zzz, emails: 1174534295@qq.com, 1309458652@qq.com"
