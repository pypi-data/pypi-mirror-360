from r3frame2.core.log import R3logger
from r3frame2.core.flags import R3flags
from r3frame2.core.status import R3status

import r3frame2.core.utils as utils

import r3frame2.core.app as app
import r3frame2.core.pipeline as pipeline
import r3frame2.core.resource as resource

import os, random
if "R3FRAME_NO_PROMT" not in os.environ:
    from r3frame2.core.quotes import *
    from r3frame2.core.version import *
    print(
        f'R3FRAME {R3FRAME_MAJOR}.{R3FRAME_MINOR}.{R3FRAME_PATCH} | "{random.choice(R3FRAME_QUOTES)}"'
    )