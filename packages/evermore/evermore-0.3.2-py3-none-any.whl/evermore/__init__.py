"""
evermore: Differentiable (binned) likelihoods in JAX.
"""

from __future__ import annotations

import datetime

__author__ = "Peter Fackeldey"
__email__ = "peter.fackeldey@princeton.edu"
__copyright__ = f"Copyright {datetime.datetime.now().year}, Peter Fackeldey"
__credits__ = ["Peter Fackeldey"]
__contact__ = "https://github.com/pfackeldey/evermore"
__license__ = "BSD-3-Clause"
__status__ = "Development"
__version__ = "0.3.2"


# expose public API

__all__ = [
    "Modifier",
    "NormalParameter",
    # explicitly expose some classes
    "Parameter",
    "__version__",
    "effect",
    "loss",
    "modifier",
    "parameter",
    "pdf",
    "sample",
    "staterror",
    "transform",
    "util",
    "visualization",
]


def __dir__():
    return __all__


from evermore import (  # noqa: E402
    loss,
    pdf,
    util,
    visualization,
)
from evermore.binned import (  # noqa: E402
    effect,
    modifier,
    staterror,
)
from evermore.binned.modifier import Modifier  # noqa: E402
from evermore.parameters import (  # noqa: E402
    parameter,
    sample,
    transform,
)
from evermore.parameters.parameter import (  # noqa: E402
    NormalParameter,
    Parameter,
)
