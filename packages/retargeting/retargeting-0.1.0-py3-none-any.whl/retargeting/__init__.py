from pathlib import Path

import numpy as np
from beartype.claw import beartype_this_package
from omegaconf import OmegaConf

beartype_this_package()


np.set_printoptions(precision=2, suppress=True)


def numpy_eval(x):
    import numpy as np  # noqa: F401, PLC0415

    return eval(x)


OmegaConf.register_new_resolver("eval", numpy_eval, replace=True)

CONF_DIR = Path(__file__).parent / "conf"


try:
    import asyncio

    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass
