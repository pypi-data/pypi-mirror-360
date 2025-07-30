# BPF Package (bisos.b) -- BISOS Python Framework
#
# Order of inclusion is important. The order reflects laying and design.

Void = type('Void', (), dict(__repr__=lambda self: 'Void'))()
Vague = type('Vague', (), dict(__repr__=lambda self: 'Vague'))()

#         ============ Layer 1 (BCF) =============
#
# BCF layer is:  BPF Common Facilities  (these have no BPF imports and provide common facilities)
#

# __import__('pkg_resources').declare_namespace(__name__)

# This has to come late or before .types  because types collides with b.types
from .utils import *
from .importFile import *

#from bisos.b import types # expose ./types.py as b.types.
from .types  import * # expose ./types.py as b.types.

from .comment import (orgMode,)


# WHY import * fails here?
from bisos.b import ast  # expose ./ast.py as b.ast. -- from .ast import *, Does not work

#         ============ Layer 2 Exposed CmndSvc Facilities (Cmnd) =============
#
# ExposedCS Facilities -- cs.Cmnd, @cs.track
#
#  b.fv, b.fto, b.fp and b.cs.* and b.io.* are intertwined.
#



from .op  import *

#from bisos.b import cs  # This is necessary here to bring over everything else
#from bisos.b.cs import inCmnd
from .cs import *

# B.IO
#from bisos.b import io
#from .io import *
from .b_io import *

from .dir import *

from .exception import *

#
#  b.fv, b.fto, b.fp and b.cs.* and b.io.* are intertwined.

from .fv import  *

from .fto import  *

#from bisos.b import fp
from .fp import  *

#         ============ Layer 3 CS Common Usage Facilities =============
#
# CsCommonUsage Facilities -- subProc, RunAs, niching, BuiltIn Commands
#

from .fpCls import  *
from .fp_csu import  *

from bisos.b.cs import ro

from .subProc import *

from .pyRunAs import *

from .niche import *

from .fpath import *

