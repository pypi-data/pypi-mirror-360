# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from pathlib import Path

import numpy as np
import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.db_utils import read_and_close


class DemandTableMetrics:
    def __init__(self, supply_file: PathLike, demand_file: PathLike):
        """
        :param supply_file: Path to the supply file corresponding to the demand file we will compute metrics for
        :param demand_file: Path to the demand file we want to compute metrics for
        """
        self.__demand_file__ = ScenarioCompression.maybe_extract(Path(demand_file))
        self.__supply_file__ = supply_file
        self.__zones = pd.DataFrame([])
        self.__loc_zn = pd.DataFrame([])

    def _build_matrices(self, dt: pd.DataFrame, matrix_names: dict):
        from aequilibrae.matrix.aequilibrae_matrix import AequilibraeMatrix
        from scipy.sparse import coo_matrix

        if self.__loc_zn.empty:
            # The location/zone relationship
            self.__loc_zn = DataTableAccess(self.__supply_file__).get("location").reset_index()[["location", "zone"]]

            # List of zones
            zn = np.sort(DataTableAccess(self.__supply_file__).get("zone").zone.to_numpy())
            self.__zones = pd.DataFrame({"zone": zn, "seq_id": np.arange(zn.shape[0])})
            self.__loc_zn = self.__loc_zn.merge(self.__zones, on="zone", how="left").drop(columns=["zone"])

        dt = dt.merge(self.__loc_zn, left_on="origin", right_on="location", how="left")
        dt = dt.drop(columns=["location"]).rename(columns={"seq_id": "origin_zone"})

        dt = dt.merge(self.__loc_zn, left_on="destination", right_on="location", how="left")
        dt = dt.drop(columns=["location"]).rename(columns={"seq_id": "destination_zone"})

        tot_ = dt.groupby(["origin_zone", "destination_zone", "tmode"]).size()
        tot_.name = "trips"
        tot = tot_.reset_index().pivot_table(
            index=["origin_zone", "destination_zone"], columns="tmode", values="trips", fill_value=0
        )
        tot = tot.reset_index().rename_axis(index=None, columns=None).rename(columns=matrix_names)
        mats = [nm for nm in tot.columns if nm not in ["origin_zone", "destination_zone"]]
        # Let's build the matrix
        num_zones = self.__zones.shape[0]
        matrix = AequilibraeMatrix()
        matrix.create_empty(zones=num_zones, matrix_names=mats, index_names=["taz"], memory_only=True)
        matrix.index[:] = self.__zones.zone.to_numpy()[:]
        orig_zones = tot.origin_zone.to_numpy()
        dest_zones = tot.destination_zone.to_numpy()
        for i, mat in enumerate(mats):
            m = coo_matrix((tot[mat].to_numpy(), (orig_zones, dest_zones)), shape=(num_zones, num_zones)).toarray()
            matrix.matrices[:, :, i] = m[:, :]
        if mats:
            matrix.computational_view(mats)

        with read_and_close(self.__demand_file__) as conn:
            fac = conn.execute("SELECT infovalue from About_Model where infoname=='abs_pop_sample_rate'").fetchone()
            factor = float(fac[0]) if fac else 1.0
        matrix.matrices /= factor

        return matrix
