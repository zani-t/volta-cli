# Dataset preprocessor & transformer for training

import pandas as pd
from pandas import DataFrame
from sklearn import preprocessing

from typing import List

from vcx.ml_utils.parser import Command

SUPPORTED_COMMANDS = {
    "DROP",
    "FILLNA",
    "FIT_TRANSFORM",
    "SET_FEATURES",
    "TRANSFORM"
}

def dictify(command: Command) -> dict[str, List[str]]:
    output = {}
    for argument in command.args:
        output[argument.name] = argument.values
    return output

def parse_value(value: str):
    decimal = False
    for char in value:
        if char.isalpha(): # Letter
            return value
        if not char.isalnum(): # Symbol
            if char != '.' or decimal == True:
                return value
            decimal = True
    if decimal:
        return float(value)

    return int(value)

def operate(data: DataFrame, command: Command) -> DataFrame:
    """ Execute single command """
    if command.name not in SUPPORTED_COMMANDS:
        # replace with real error
        raise Exception
    if command.name == "DROP":
        command_dict = dictify(command)
        # DECLARE VARIABLES BASED ON ARGUMENTS GIVEN
        labels, axis = command_dict["FEATURES"], int(command_dict["AXIS"][0])
        data = data.drop(labels=labels, axis=axis)
    elif command.name == "FILLNA":
        command_dict = dictify(command)
        cols, value, inplace = (
            command_dict["FEATURES"],
            parse_value(command_dict["VALUE"][0]),
            command_dict.get("INPLACE", ["False"])[0],
        )
        for col in cols:
            data[col].fillna(
                value=(data[col].median() if value == "Median" else value),
                inplace=True if inplace == "True" else False,
            )
    elif command.name == "FIT_TRANSFORM":
        le = preprocessing.LabelEncoder()
        command_dict = dictify(command)
        cols = command_dict["FEATURES"] # OTHER PARAMS
        for col in cols:
            data[col] = le.fit_transform(data[col])
    elif command.name == "SET_FEATURES":
        command_dict = dictify(command)
        data = data[command_dict["FEATURES"]]
    elif command.name == "TRANSFORM":
        pass

    return data

def process(data: DataFrame, script: List[Command]) -> DataFrame:
    """ Run loop all preprocessing script commands """
    for command in script:
        data = operate(data, command)
    return data