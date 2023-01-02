# Dataset preprocessor & transformer for training

import pandas as pd
from pandas import DataFrame

from typing import List

from vcx.ml_utils.parser import Command

SUPPORTED_COMMANDS = {
    "DROP",
    "FILLNA",
    "FIT_TRANSFORM",
    "SET_LABEL",
    "TRANSFORM"
}

def operate(data: DataFrame, command: Command) -> DataFrame:
    """ Execute single command """
    if command.name not in SUPPORTED_COMMANDS:
        # replace with real error
        raise Exception
    if command.name == "DROP":
        # Change args property to dictionary for instant lookup
        labels=command.args
        data.drop(labels=labels)

    return data

def process(data: DataFrame, script: List[Command]) -> DataFrame:
    """ Run loop all preprocessing script commands """
    for command in script:
        data = operate(data, command)
    return data