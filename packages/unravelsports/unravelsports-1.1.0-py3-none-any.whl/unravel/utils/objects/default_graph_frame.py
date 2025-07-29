import numpy as np

import warnings

from typing import Union

from dataclasses import dataclass, field

from ..exceptions.warnings import QualityCheckWarning

from spektral.data import Graph

from ..features import (
    PredictionLabelType,
    make_sparse,
)
from .default_graph_settings import DefaultGraphSettings
from .default_tracking import DefaultTrackingModel


@dataclass
class DefaultGraphFrame:
    frame_id: int
    data: DefaultTrackingModel
    settings: DefaultGraphSettings
    graph_id: Union[str, int]
    label: Union[int, bool]
    graph_data: dict = field(init=False, repr=False, default=None)

    def __post_init__(self):
        A, A_delaunay = self._adjaceny_matrix()
        X = self._node_features()
        E = self._edge_features(A, A_delaunay)

        if self.settings.pad:
            X, A, E = self._pad(x=X, a=A, e=E)

        if self.settings.random_seed is not False:
            X, A, E = self._shuffle(x=X, a=A, e=E)
            if not self.settings.label_type == PredictionLabelType.BINARY:
                raise NotImplementedError(
                    "Need to potentially implement a shuffle for Y to follow the shuffling of X, A and E."
                )

        sparse_A = make_sparse(A)
        Y = self._label()

        if self._quality_check(X, E):
            self.graph_data = dict(x=X, a=sparse_A, e=E, y=Y, id=self.graph_id)

    def to_spektral_graph(self) -> Graph:
        if self.graph_data:
            return Graph(
                x=self.graph_data["x"],
                a=self.graph_data["a"],
                e=self.graph_data["e"],
                y=self.graph_data["y"],
                id=self.graph_id,
            )
        else:
            return None

    def _label(self):
        if self.settings.label_type == PredictionLabelType.BINARY:
            return np.asarray([int(self.label)])
        else:
            raise NotImplementedError("Label should be PredictionLabelType.BINARY")

    def _adjaceny_matrix(self):
        """
        Create adjeceny matrices. If we specify the Adjaceny Matrix type to be Delaunay it's created as the 'general' A,
        else we create a seperate one as A_delaunay.
        This way we can use the Delaunay matrix in the Edge Features if it's not used as the Adj Matrix
        """
        raise NotImplementedError()

    def _node_features(self):
        raise NotImplementedError()

    def _edge_features(self, A, A_delaunay):
        raise NotImplementedError()

    def _quality_check(self, X, E):
        if self.settings.boundary_correction is not None:
            if (np.max(X) <= 1) or (np.min(X) >= -1):
                warnings.warn(
                    f"""Node Feature(s) outside boundary for frame={self.frame_id}, skipping...""",
                    QualityCheckWarning,
                )
                return False
            if (np.max(E) <= 1) or (np.min(E) >= -1):
                warnings.warn(
                    f"""Edge Feature(s) outside boundary for frame={self.frame_id}, skipping...""",
                    QualityCheckWarning,
                )
                return False
        return True

    def _shuffle(self, x, a, e):
        if isinstance(self.settings.random_seed, int):
            np.random.seed(self.settings.random_seed)
        elif self.settings.random_seed == True:
            np.random.seed()
        else:
            pass

        # Generate a random permutation of node indices
        num_nodes = x.shape[0]
        permutation = np.random.permutation(num_nodes)

        # Permute the rows and columns of the adjacency matrix
        a_shuffled = a[permutation, :][:, permutation]

        # Permute the rows of the node features matrix

        x_shuffled = x[permutation]
        # Adjust the edge features matrix
        # Get the indices of non-zero elements in the original adjacency matrix
        row, col = np.nonzero(a)

        # Map the original indices to the new shuffled indices
        row_shuffled = permutation[row]
        col_shuffled = permutation[col]

        # Create a dictionary to map from original index pairs to new index pairs
        index_mapping = {
            (r, c): (rs, cs)
            for r, c, rs, cs in zip(row, col, row_shuffled, col_shuffled)
        }

        # Sort the new index pairs to ensure consistency
        sorted_indices = sorted(index_mapping.values())

        # Create an array of edge features based on the sorted indices
        e_shuffled = np.zeros_like(e, dtype=float)

        # Populate the new edge features matrix
        for idx, (r, c) in enumerate(sorted_indices):
            original_index = list(index_mapping.values()).index((r, c))
            e_shuffled[idx] = e[original_index]

        return x_shuffled, a_shuffled, e_shuffled

    def _pad(self, x, a, e):
        n_node_features = x.shape[1]
        n_edge_features = e.shape[1]

        max_edges = self.settings.pad_settings.max_edges
        max_nodes = self.settings.pad_settings.max_nodes

        # Padding node features
        pad_x = np.zeros((max_nodes, n_node_features))
        pad_x[: x.shape[0], : x.shape[1]] = x

        # Padding adjacency matrix
        pad_a = np.zeros((max_nodes, max_nodes))
        pad_a[: a.shape[0], : a.shape[1]] = a

        # Padding edge features
        pad_e = np.zeros((max_edges, n_edge_features))
        pad_e[: e.shape[0], : e.shape[1]] = e

        return pad_x, pad_a, pad_e
