"""
Graphdict
========

Graphdict is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

See https://networkx.org for complete documentation.
"""

__version__ = "3.4.13"


def __getattr__(name):
    """Remove functions and provide informative error messages."""
    if name == "nx_yaml":
        raise ImportError(
            "\nThe nx_yaml module has been removed from graphdict.\n"
            "Please use the `yaml` package directly for working with yaml data.\n"
            "For example, a graphdict.Graph `G` can be written to and loaded\n"
            "from a yaml file with:\n\n"
            "    import yaml\n\n"
            "    with open('path_to_yaml_file', 'w') as fh:\n"
            "        yaml.dump(G, fh)\n"
            "    with open('path_to_yaml_file', 'r') as fh:\n"
            "        G = yaml.load(fh, Loader=yaml.Loader)\n\n"
            "Note that yaml.Loader is considered insecure - see the pyyaml\n"
            "documentation for further details.\n\n"
        )
    if name == "read_yaml":
        raise ImportError(
            "\nread_yaml has been removed from graphdict, please use `yaml`\n"
            "directly:\n\n"
            "    import yaml\n\n"
            "    with open('path', 'r') as fh:\n"
            "        yaml.load(fh, Loader=yaml.Loader)\n\n"
            "Note that yaml.Loader is considered insecure - see the pyyaml\n"
            "documentation for further details.\n\n"
        )
    if name == "write_yaml":
        raise ImportError(
            "\nwrite_yaml has been removed from graphdict, please use `yaml`\n"
            "directly:\n\n"
            "    import yaml\n\n"
            "    with open('path_for_yaml_output', 'w') as fh:\n"
            "        yaml.dump(G_to_be_yaml, path_for_yaml_output, **kwds)\n\n"
        )
    raise AttributeError(f"module {__name__} has no attribute {name}")


# These are import orderwise
from graphdict.exception import *

from graphdict import utils

from graphdict import classes
from graphdict.classes import filters
from graphdict.classes import *

from graphdict import convert
from graphdict.convert import *

from graphdict import convert_matrix
from graphdict.convert_matrix import *

from graphdict import relabel
from graphdict.relabel import *

from graphdict import generators
from graphdict.generators import *

from graphdict import readwrite
from graphdict.readwrite import *

# Need to test with SciPy, when available
from graphdict import algorithms
from graphdict.algorithms import *

from graphdict import linalg
from graphdict.linalg import *

from graphdict.testing.test import run as test

from graphdict import drawing
from graphdict.drawing import *
