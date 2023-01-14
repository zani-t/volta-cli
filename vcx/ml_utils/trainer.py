# Model object initializer & trainer

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
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
    label: str | None,
    test_size: float,
    rs_ds: int | None,
    rs_m: int | None,
    max_iter: int | None,
    penalty: str,
    kernel: str,
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

    if (arch == "LogisticRegression") or (arch == "LogReg"):
        if not label:
            # ADD NO LABEL ERROR
            raise Exception
        y = data[label]
        X = data.drop(label, axis=1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=rs_ds)
        clf = LogisticRegression(penalty=penalty, random_state=rs_m, max_iter=max_iter).fit(X_train, y_train)
        print(clf.score(X_test, y_test))
    
    if (arch == "SupportVectorMachine") or (arch == "SVM"):
        if not label:
            # ADD NO LABEL ERROR
            raise Exception
        y = data[label]
        X = data.drop(label, axis=1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=rs_ds)
        clf = SVC(kernel=kernel, random_state=rs_m).fit(X_train, y_train) # ADD REGULARIZATION C
        print(clf.score(X_test, y_test))

    # Display eval metric and prompt user to save

    return SUCCESS