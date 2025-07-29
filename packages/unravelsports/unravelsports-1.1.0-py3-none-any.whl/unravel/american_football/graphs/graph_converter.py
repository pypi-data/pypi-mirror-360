from warnings import warn

from dataclasses import dataclass

import polars as pl
import numpy as np

from typing import List, Optional

from spektral.data import Graph

from ..dataset import BigDataBowlDataset, Group, Column, Constant

from .graph_settings import (
    AmericanFootballGraphSettings,
    AmericanFootballPitchDimensions,
)
from .features import (
    compute_node_features,
    compute_edge_features,
    compute_adjacency_matrix,
)

from ...utils import *


@dataclass(repr=True)
class AmericanFootballGraphConverter(DefaultGraphConverter):
    """
    Converts our dataset TrackingDataset into an internal structure

    Attributes:
        dataset (BigDataBowlDataset): BigDataBowlDataset.
        chunk_size (int): Used to batch convert Polars into Graphs
        attacking_non_qb_node_value (float): Value between 0 and 1 to assign any attacking team player who is not the QB
        graph_features_as_node_features_columns (list):
            List of columns in the dataset that are Graph level features (e.g. team strength rating, win probabilities etc)
            we want to add to our model. They will be recorded as Node Features on the "football" node.
            They should be joined to the BigDataBowlDataset.data dataframe such that
            each Group in the group_by has the same value per column. We take the first value of the group, and assign this as a
            "graph level feature" to the ball node.
    """

    def __init__(
        self,
        dataset: BigDataBowlDataset,
        chunk_size: int = 2_000,
        attacking_non_qb_node_value: float = 0.1,
        graph_feature_cols: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if not isinstance(dataset, BigDataBowlDataset):
            raise Exception("'dataset' should be an instance of BigDataBowlDataset")

        self.label_column: str = (
            self.label_col if self.label_col is not None else dataset._label_column
        )
        self.graph_id_column: str = (
            self.graph_id_col
            if self.graph_id_col is not None
            else dataset._graph_id_column
        )

        self.sample_rate = kwargs.get("sample_rate", None)
        self.chunk_size = chunk_size
        self.attacking_non_qb_node_value = attacking_non_qb_node_value
        self.graph_feature_cols = graph_feature_cols
        self.settings = self._apply_graph_settings(settings=dataset.settings)

        self.dataset: pl.DataFrame = dataset.data

        self._sport_specific_checks()

        self._sample()
        self._shuffle()

    def _sample(self):
        if self.sample_rate is None:
            return
        else:
            self.dataset = self.dataset.filter(
                pl.col(Column.FRAME_ID) % (1.0 / self.sample_rate) == 0
            )

    def _sport_specific_checks(self):
        def __remove_with_missing_values(min_object_count: int = 10):
            cs = (
                self.dataset.group_by(Group.BY_FRAME)
                .agg(pl.len().alias("size"))
                .filter(
                    pl.col("size") < min_object_count
                )  # Step 2: Keep groups with size < 10
            )

            self.dataset = self.dataset.join(cs, on=Group.BY_FRAME, how="anti")
            if len(cs) > 0:
                warn(
                    f"Removed {len(cs)} frames with less than {min_object_count} objects...",
                    UserWarning,
                )

        def __remove_with_missing_football():
            cs = (
                self.dataset.group_by(Group.BY_FRAME)
                .agg(
                    [
                        pl.len().alias("size"),  # Count total rows in each group
                        pl.col(Column.TEAM_ID)
                        .filter(pl.col(Column.TEAM_ID) == Constant.BALL)
                        .count()
                        .alias("football_count"),  # Count rows where team == 'football'
                    ]
                )
                .filter(
                    (pl.col("football_count") == 0)
                )  # Step 2: Keep groups with size < 10 and no "football"
            )
            self.dataset = self.dataset.join(cs, on=Group.BY_FRAME, how="anti")
            if len(cs) > 0:
                warn(
                    f"Removed {len(cs)} frames with a missing '{Constant.BALL}' object...",
                    UserWarning,
                )

        if not isinstance(self.label_column, str):
            raise Exception("'label_col' should be of type string (str)")

        if not isinstance(self.graph_id_column, str):
            raise Exception("'graph_id_col' should be of type string (str)")

        if not isinstance(self.chunk_size, int):
            raise Exception("chunk_size should be of type integer (int)")

        if not self.label_column in self.dataset.columns and not self.prediction:
            raise Exception(
                "Please specify a 'label_col' and add that column to your 'dataset' or set 'prediction=True' if you want to use the converted dataset to make predictions on."
            )

        if not self.graph_id_column in self.dataset.columns:
            raise Exception(
                "Please specify a 'graph_id_col' and add that column to your 'dataset' ..."
            )

        # Parameter Checks
        if not isinstance(self.attacking_non_qb_node_value, (int, float)):
            raise Exception(
                "'attacking_non_qb_node_value' should be of type float or integer (int)"
            )

        __remove_with_missing_values(min_object_count=10)
        __remove_with_missing_football()

    def _apply_graph_settings(self, settings):
        return AmericanFootballGraphSettings(
            pitch_dimensions=settings.pitch_dimensions,
            max_player_speed=settings.max_player_speed,
            max_ball_speed=settings.max_ball_speed,
            max_ball_acceleration=settings.max_ball_acceleration,
            max_player_acceleration=settings.max_player_acceleration,
            self_loop_ball=self.self_loop_ball,
            adjacency_matrix_connect_type=self.adjacency_matrix_connect_type,
            adjacency_matrix_type=self.adjacency_matrix_type,
            label_type=self.label_type,
            defending_team_node_value=self.defending_team_node_value,
            attacking_non_qb_node_value=self.attacking_non_qb_node_value,
            random_seed=self.random_seed,
            pad=self.pad,
            verbose=self.verbose,
        )

    @property
    def _exprs_variables(self):
        exprs_variables = [
            Column.X,
            Column.Y,
            Column.SPEED,
            Column.ACCELERATION,
            Column.ORIENTATION,
            Column.DIRECTION,
            Column.TEAM_ID,
            Column.POSITION_NAME,
            Column.BALL_OWNING_TEAM_ID,
            Column.HEIGHT_CM,
            Column.WEIGHT_KG,
            self.graph_id_column,
            self.label_column,
        ]
        exprs = (
            exprs_variables
            if self.graph_feature_cols is None
            else exprs_variables + self.graph_feature_cols
        )
        return exprs

    def _compute(self, args: List[pl.Series]) -> dict:
        d = {col: args[i].to_numpy() for i, col in enumerate(self._exprs_variables)}
        frame_id = args[-1][0]

        if self.graph_feature_cols is not None:
            failed = [
                col
                for col in self.graph_feature_cols
                if not np.all(d[col] == d[col][0])
            ]
            if failed:
                raise ValueError(
                    f"""graph_feature_cols contains multiple different values for a group in the groupby ({Group.BY_FRAME}) selection for the columns {failed}. Make sure each group has the same values per individual column."""
                )

        graph_features = (
            np.asarray([d[col] for col in self.graph_feature_cols]).T[0]
            if self.graph_feature_cols
            else None
        )

        if not np.all(d[self.graph_id_column] == d[self.graph_id_column][0]):
            raise Exception(
                "GraphId selection contains multiple different values. Make sure each graph_id is unique by at least game_id and frame_id..."
            )

        if not self.prediction and not np.all(
            d[self.label_column] == d[self.label_column][0]
        ):
            raise Exception(
                """Label selection contains multiple different values for a single selection (group by) of game_id and frame_id, 
                make sure this is not the case. Each group can only have 1 label."""
            )

        adjacency_matrix = compute_adjacency_matrix(
            team=d[Column.TEAM_ID],
            possession_team=d[Column.BALL_OWNING_TEAM_ID],
            settings=self.settings,
        )
        edge_features = compute_edge_features(
            adjacency_matrix=adjacency_matrix,
            p=np.stack((d[Column.X], d[Column.Y]), axis=-1),
            s=d[Column.SPEED],
            a=d[Column.ACCELERATION],
            dir=d[Column.DIRECTION],
            o=d[Column.ORIENTATION],
            team=d[Column.TEAM_ID],
            settings=self.settings,
        )
        node_features = compute_node_features(
            x=d[Column.X],
            y=d[Column.Y],
            s=d[Column.SPEED],
            a=d[Column.ACCELERATION],
            dir=d[Column.DIRECTION],
            o=d[Column.ORIENTATION],
            team=d[Column.TEAM_ID],
            official_position=d[Column.POSITION_NAME],
            possession_team=d[Column.BALL_OWNING_TEAM_ID],
            height=d[Column.HEIGHT_CM],
            weight=d[Column.WEIGHT_KG],
            graph_features=graph_features,
            settings=self.settings,
        )
        return {
            "e": pl.Series(
                [edge_features.tolist()], dtype=pl.List(pl.List(pl.Float64))
            ),
            "x": pl.Series(
                [node_features.tolist()], dtype=pl.List(pl.List(pl.Float64))
            ),
            "a": pl.Series(
                [adjacency_matrix.tolist()], dtype=pl.List(pl.List(pl.Int32))
            ),
            "e_shape_0": edge_features.shape[0],
            "e_shape_1": edge_features.shape[1],
            "x_shape_0": node_features.shape[0],
            "x_shape_1": node_features.shape[1],
            "a_shape_0": adjacency_matrix.shape[0],
            "a_shape_1": adjacency_matrix.shape[1],
            self.graph_id_column: d[self.graph_id_column][0],
            self.label_column: d[self.label_column][0],
            "frame_id": frame_id,
        }

    def _convert(self):
        # Group and aggregate in one step
        return (
            self.dataset.group_by(Group.BY_FRAME, maintain_order=True)
            .agg(
                pl.map_groups(
                    exprs=self._exprs_variables + [Column.FRAME_ID],
                    function=self._compute,
                    return_dtype=self.return_dtypes,
                ).alias("result_dict")
            )
            .with_columns(
                [
                    *[
                        pl.col("result_dict").struct.field(f).alias(f)
                        for f in [
                            "a",
                            "e",
                            "x",
                            self.graph_id_column,
                            self.label_column,
                            "frame_id",
                        ]
                    ],
                    *[
                        pl.col("result_dict")
                        .struct.field(f"{m}_shape_{i}")
                        .alias(f"{m}_shape_{i}")
                        for m in ["a", "e", "x"]
                        for i in [0, 1]
                    ],
                ]
            )
            .drop("result_dict")
        )
