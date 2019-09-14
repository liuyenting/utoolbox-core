import logging
from pprint import pprint

import networkx as nx

from utoolbox.stitching.error import NotConsolidatedError

__all__ = ["Sandbox"]

logger = logging.getLogger(__name__)


class Sandbox(object):
    def __init__(self, datastore):
        self._datastore = datastore
        self._links = nx.Graph()

        # populate the graph
        self._links.add_nodes_from(datastore.keys())

        # only exists after consolidation
        self._sequence = None

    @property
    def shape(self):
        """Current full extent of the sandbox."""
        pass

    @property
    def datastore(self):
        return self._datastore

    @property
    def sequence(self):
        # TODO raise error until not None
        return self._sequence

    def link(self, ref, target, shift, weight=1.0):
        self._links.add_edge(ref, target, weight=weight, shift=shift)

    def consolidate(self):
        """Fix edge weights into fusion sequence."""
        # build graph
        mst = nx.minimum_spanning_tree(self._links)

        # TODO determine bounding box
        for edge in mst.edges(data=True):
            pprint(edge)

        # TODO calculate shift list

    def result(self, tiles=None):
        """Fuse the result based on fusion sequence."""
        if self.sequence is None:
            raise NotConsolidatedError("please consolidate the sandbox first")

        # TODO determine overlaps

    def _determine_bounding_box(self):
        pass
