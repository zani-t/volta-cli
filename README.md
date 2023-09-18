# Volta CLI

Volta CLI is an unfinished interface that was intended for users to upload a dataset, train a scikit-learn based ML model with custom hyperparameters, and deploy the model as a Flask-based web server endpoint, all from the command line.

The project was created using Python and MySQL, along with the Poetry package, and MySQL connector and Typer libraries.

**Functions implemented included:**
- Login and logout of a MySQL server
- Creation, modification, and deletion of entries in a MySQL database
- Raw MySQL executed through command line
- Creation of pandas-based model preprocessing scripts (capabilities include drop, fillna, fit_transform, etc.)
- Training of logistic regression, SVM, and random forest models (hyperparamters include random state, # iterations, regualarization penalty, SVM kernel)
- Dataset previews

**Functions not implemented included:**
- Saving of models
- Deployment to Flask endpoint
- HTTP requests processed by Flask
- More preprocessing commands
- And several other minor features.

**An example process:**  
vcx status  
vcx login -h [hostname] -u [username]  
vcx start  
vcx init  
  
vcx cdataset -n titanic -l local -a [address]  
vcx cscript -n script1 -ds titanic  
vcx cmodel -n titanic_logreg -ds titanic -a LogisticRegression -p script1  
  
vcx enterscript -n script1  
vcx pushscript  
DROP $LABELS &Ticket,Cabin,Name,PassengerID $AXIS &1  
  
vcx train -n titanic_logreg -ds titanic -s script1 -label Survived -testsize 0.15 -maxiter 500 -penalty l2  
 
...  
  
Commit times are inaccurate as most of this was programmed on a VM that is 7 months behind...  
  
Volta CLI was named after the river Volta in Ghana and Burkina Faso:  
  
![image](https://github.com/zani-t/volta-cli/assets/106849931/db187753-3855-4a34-be6f-f8df7e93a311)
  
