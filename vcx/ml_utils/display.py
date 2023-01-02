# Model attribute display

import pandas as pd

from vcx.server import mysql_server
from vcx import (
    Login, DatasetResponsePy,
    ERR_PANDAS_READ, SUCCESS
)

""" PREPROCESSING """

# List all columns/features
def list_columns(
    login: Login,
    name: int,
    # optional parameter list specific columns
) -> DatasetResponsePy:
    """ List dataset columns """
    # Get dataset address
    location, address, getds_error = mysql_server.getdataset(login, name=name)
    if getds_error:
        return getds_error

    try:
        # ONLY LOCAL SUPPORTED ?
        data = pd.read_csv(address)
        return ('\n'.join(data), SUCCESS)
    except Exception as e:
        print(e)
        return (None, ERR_PANDAS_READ)

# List dimensions

# Head (display top few rows)

# Return median/s, etc.

# [Display graphics via plotext]

""" EVALUATION """

# Confusion matrix

# ...