# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from os import PathLike

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.transit.transit_elements.agency import Agency


def read_agencies(conn: sqlite3.Connection, network_file: PathLike):
    data = DataTableAccess(network_file).get("transit_agencies", conn)
    return [Agency(network_file).from_row(dt) for _, dt in data.iterrows() if dt.agency_id > 1]
