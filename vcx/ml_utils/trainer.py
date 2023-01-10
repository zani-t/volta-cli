# Model object initializer & trainer

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from vcx.ml_utils import parser, preprocessor
from vcx.server import mysql_server
from vcx import (
    Login,
    SUCCESS
)

def train(
    login: Login,
    name: str,
    ds_name: str,
    script_name: str,
    label: str,
    test_size: float,
    penalty: str,
    max_iter: int,
) -> int:
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
    
    raw_script, getscript_error = mysql_server.getscript(login, script_name)
    if getscript_error:
        return getscript_error
    script = parser.parse_to_commands(raw_script)

    data = preprocessor.process(raw_data, script)

    # Initialize and train model
    arch = mysql_model[5]
    if arch == "LogisticRegression":
        if not label:
            # ADD NO LABEL ERROR
            raise Exception
        y = data[label]
        X = data.drop(label, axis=1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        clf = LogisticRegression(penalty=penalty, random_state=0, max_iter=max_iter).fit(X_train, y_train)

    # Display eval metric and prompt user to save
    predictions = clf.predict(X_test)
    print(accuracy_score(y_test, predictions))

    return SUCCESS
    # vcx train -n titanic_logreg_0.1 -ds TitanicDataset -s TitanicScript -l Survived -mi 1000