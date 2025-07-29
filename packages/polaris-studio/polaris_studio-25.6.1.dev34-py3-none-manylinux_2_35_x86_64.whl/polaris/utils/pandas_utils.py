# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from functools import reduce
import numpy as np


def filter_df(df, includes):
    for col, constraint in includes.items():
        if isinstance(constraint, str):
            df = df[(df[col].str.upper() == constraint.upper())]
        elif isinstance(constraint, int):
            df = df[(df[col] == constraint)]
        elif isinstance(constraint, list):
            if isinstance(constraint[0], str):
                df = df[reduce(np.bitwise_or, [df[col].str.upper() == c.upper() for c in constraint])]
            elif isinstance(constraint[0], int):
                df = df[reduce(np.bitwise_or, [df[col] == c for c in constraint])]
            else:
                raise TypeError("Don't know how to handle a list of that")
        else:
            raise TypeError(f"Don't know how to handle a constraint of type {type(constraint)}")

    return df


def stochastic_round(x, decimals=0):
    frac, whole = np.modf(x * 10**decimals)
    rand = np.random.rand(x.size)
    return np.where(rand < frac, whole + 1, whole) / 10**decimals
