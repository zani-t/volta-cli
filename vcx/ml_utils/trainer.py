# Model object initializer & trainer

import pandas as pd

from vcx.ml_utils import parser, preprocessor
from vcx.server import mysql_server
from vcx import (
    Login,
    SUCCESS
)

def train(login: Login, name: str, ds_name: str, script_name: str) -> int:
    """ Train model """
    # Retrieve model
    mysql_model, mysql_model_error = mysql_server.getmodel(login, name)
    if mysql_model_error:
        return mysql_model_error

    # Retrieve and preprocess dataset
    location, address, getds_error = mysql_server.getdataset(login, ds_name)
    if getds_error:
        return getds_error
    raw_data = pd.read_csv(address)
    
    raw_script, getscript_error = mysql_server.getscript(login)
    if getscript_error:
        return getscript_error
    script = parser.parse_to_objects(raw_script)

    data = preprocessor.process(raw_data, script)

    # Initialize and train model
    arch = mysql_model[7]

    # Display eval metric and prompt user to save

    return SUCCESS