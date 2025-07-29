# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import shutil
import sys
from os.path import join, isdir
from pathlib import Path
from tempfile import gettempdir
from uuid import uuid4

from polaris import Polaris
from polaris.demand.checker.demand_checker import DemandChecker
from polaris.network.checker.supply_checker import SupplyChecker
from polaris.project.project_restorer import restore_project_from_csv
from polaris.utils.global_checker import GlobalChecker


def critical_network_tests(city: str, model_text_folder: str, model_dir=None):
    model_dir = model_dir or join(gettempdir(), uuid4().hex)

    restore_project_from_csv(model_dir, model_text_folder, city, overwrite=True)
    shutil.copytree(Path(model_text_folder) / "supply", Path(model_dir) / "supply", dirs_exist_ok=True)

    if isdir(Path(model_text_folder) / "demand"):
        shutil.copytree(Path(model_text_folder) / "demand", Path(model_dir) / "demand", dirs_exist_ok=True)

    model_dir = Path(model_dir)
    pol = Polaris.from_dir(model_dir)

    SupplyChecker(pol.supply_file).has_critical_errors(True)
    DemandChecker(pol.demand_file).has_critical_errors(True)
    GlobalChecker(pol).has_critical_errors(True)


if __name__ == "__main__":
    critical_network_tests(sys.argv[1], sys.argv[2])
