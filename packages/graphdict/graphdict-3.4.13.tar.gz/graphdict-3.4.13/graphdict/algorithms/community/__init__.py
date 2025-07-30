"""Functions for computing and measuring community structure.

The functions in this class are not imported into the top-level
:mod:`networkx` namespace. You can access these functions by importing
the :mod:`networkx.algorithms.community` module, then accessing the
functions as attributes of ``community``. For example::

    >>> from graphdict.algorithms import community
    >>> G = nx.barbell_graph(5, 1)
    >>> communities_generator = community.girvan_newman(G)
    >>> top_level_communities = next(communities_generator)
    >>> next_level_communities = next(communities_generator)
    >>> sorted(map(sorted, next_level_communities))
    [[0, 1, 2, 3, 4], [5], [6, 7, 8, 9, 10]]

"""
from graphdict.algorithms.community.asyn_fluid import *
from graphdict.algorithms.community.centrality import *
from graphdict.algorithms.community.kclique import *
from graphdict.algorithms.community.kernighan_lin import *
from graphdict.algorithms.community.label_propagation import *
from graphdict.algorithms.community.lukes import *
from graphdict.algorithms.community.modularity_max import *
from graphdict.algorithms.community.quality import *
from graphdict.algorithms.community.community_utils import *
