import pandas as pd
import numpy as np
import copy
import sklearn
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import matthews_corrcoef
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn import linear_model
import matplotlib.pyplot as plt

def countyConvert(input1,input2,ouput):#@input1: csv file @input2: column header @output: output file name
	a=input.input2.unique() #take all the unqiue attribute in the column
	with open(output, "a") as f:
		counter = 0 
		for i in a: #output in a file that is a usable dictionary format
			f.write("'"+i +"' : "+ str(counter)+ " , ")
			counter+=1
	f.close() #used to convert all county name into a number that can be used as dictionary

def modelGen(x_train, y_train, state=0, mdepth = 0, nEstimators = 100 ): #state 0 DecisionTreeClassifier, state 1 RandomForestClassifier
	if state == 0:
		model = tree.DecisionTreeClassifier(max_depth = mdepth)
		model.fit(x_train, y_train)
	elif state == 1:
		model = sklearn.ensemble.RandomForestClassifier(n_estimators = nEstimators, max_depth = mdepth)
		model.fit(x_train, y_train)
	return model

def predictGen(model,x_test,y_test): #predict and print the accuracy score and correlation, return matthew correlation if needed
	y_predict = model.predict(x_test)
	a_score = accuracy_score(y_test,y_predict) #accuracy score
	c_mat = pd.DataFrame(confusion_matrix(y_test,y_predict), columns = ['P UL','P L', 'P H','P VH'], index = ['T UL','T L', 'T H','T VH']) #correlation matrix
	mat_corr = matthews_corrcoef(y_test,y_predict)
	print("Accuracy Score: " + str(a_score))
	print("Matthew Correlation: "+ str(mat_corr))
	return mat_corr, c_mat

def modelCSV(trainFile,testFile,iCol): #load csv data
	dfTrain = pd.read_csv(trainFile, index_col=iCol)
	train_obj = len(dfTrain)
	dfTest = pd.read_csv(testFile, index_col=iCol)
	#labeled column
	colName = ['County','Year','DI.Avg.','Yield','Soil..WA.','RF.May.','RF.June.','RF.July.','RF.Aug.','RF.Sep.','TMax.May.','TMin..May.','TMax.June.','TMin.June.','TMax.July.','TMin.July.','TMax.Aug.','TMin.Aug.','TMax.Sep.','TMin.Sep.']
	yieldDict = {'Very Low':0,'Low':1,'High':2,'Very High':3}
	countyDict = {'Adair' : 0 , 'Adams' : 1 , 'Allamakee' : 2 , 'Appanoose' : 3 , 'Audubon' : 4 , 'Benton' : 5 , 'Black Hawk' : 6 , 'Boone' : 7 , 'Bremer' : 8 , 'Buchanan' : 9 , 'Buena Vista' : 10 , 'Butler' : 11 , 'Calhoun' : 12 , 'Carroll' : 13 , 'Cass' : 14 , 'Cedar' : 15 , 'Cerro Gordo' : 16 , 'Cherokee' : 17 , 'Chickasaw' : 18 , 'Clarke' : 19 , 'Clay' : 20 , 'Clayton' : 21 , 'Clinton' : 22 , 'Crawford' : 23 , 'Dallas' : 24 , 'Davis' : 25 , 'Decatur' : 26 , 'Delaware' : 27 , 'Des Moines' : 28 , 'Dickinson' : 29 , 'Dubuque' : 30 , 'Emmet' : 31 , 'Fayette' : 32 , 'Floyd' : 33 , 'Franklin' : 34 , 'Fremont' : 35 , 'Greene' : 36 , 'Grundy' : 37 , 'Guthrie' : 38 , 'Hamilton' : 39 , 'Hancock' : 40 , 'Hardin' : 41 , 'Harrison' : 42 , 'Henry' : 43 , 'Howard' : 44 , 'Humboldt' : 45 , 'Ida' : 46 , 'Iowa' : 47 , 'Jackson' : 48 , 'Jasper' : 49 , 'Jefferson' : 50 , 'Johnson' : 51 , 'Jones' : 52 , 'Keokuk' : 53 , 'Kossuth' : 54 , 'Lee' : 55 , 'Linn' : 56 , 'Louisa' : 57 , 'Lucas' : 58 , 'Lyon' : 59 , 'Madison' : 60 , 'Mahaska' : 61 , 'Marion' : 62 , 'Marshall' : 63 , 'Mills' : 64 , 'Mitchell' : 65 , 'Monona' : 66 , 'Monroe' : 67 , 'Montgomery' : 68 , 'Muscatine' : 69 , 'O\'Brien' : 70 , 'Osceola' : 71 , 'Page' : 72 , 'Palo Alto' : 73 , 'Plymouth' : 74 , 'Pocahontas' : 75 , 'Polk' : 76 , 'Pottawattamie' : 77 , 'Poweshiek' : 78 , 'Ringgold' : 79 , 'Sac' : 80 , 'Scott' : 81 , 'Shelby' : 82 , 'Sioux' : 83 , 'Story' : 84 , 'Tama' : 85 , 'Taylor' : 86 , 'Union' : 87 , 'Van Buren' : 88 , 'Wapello' : 89 , 'Warren' : 90 , 'Washington' : 91 , 'Wayne' : 92 , 'Webster' : 93 , 'Winnebago' : 94 , 'Winneshiek' : 95 , 'Woodbury' : 96 , 'Worth' : 97 , 'Wright' : 98 }
	#train file labeling
	dfTrain = dfTrain[colName]
	dfTrain['Yield']=dfTrain['Yield'].map(yieldDict)
	dfTrain['County'] = dfTrain['County'].map(countyDict)
	#test file labeling
	dfTest = dfTest[colName]
	dfTest['Yield']=dfTest['Yield'].map(yieldDict)
	dfTest['County'] = dfTest['County'].map(countyDict)
	#concate into one
	dataset = pd.concat(objs=[dfTrain,dfTest],axis = 0)
	#create dummy category to make sure both have same feature
	dataset = pd.get_dummies(dataset)
	#split them again
	encoder = OneHotEncoder(categorical_features = [0])
	#create train
	X = dataset.drop('Yield',axis=1)
	Y = dataset['Yield']
	encoder.fit(X)
	x_transformed = encoder.transform(X).toarray()
	#create train
	x_train = copy.copy(x_transformed[:train_obj])
	y_train = Y[:train_obj]
	#create test
	x_test = copy.copy(x_transformed[train_obj:])
	y_test = Y[train_obj:]
	return x_train,y_train,x_test,y_test
	
def kRetrain(x,y,fold):
	#create folds
	kf = KFold(n_splits=fold) 
	mse = []
	#spilit the models
	for train_index, test_index in kf.split(x):
		x_train,x_test = x[train_index],x[test_index]
		y_train,y_test = y[train_index],y[test_index]
		model = linear_model.LinearRegression()
		model.fit(x_train,y_train.ravel())
		y_predict = model.predict(x_test)
		mse.append(mean_squared_error(y_test.ravel(),y_predict))
	return mse

def rmseCSV(fileA,fileB):
	#read file
	dfA = pd.read_csv(fileA, header = None)
	#combine the two chromosome to represent the one individuals
	dfAa = dfA[0::2]
	dfAa = dfAa.reset_index()
	dfAa = dfAa.drop(['index'],axis=1)
	dfAb = dfA[1::2]
	dfAb = dfAb.reset_index()
	dfAb = dfAb.drop(['index'],axis=1)
	dfA = pd.concat([dfAa,dfAb],axis=1)
	dfA = dfA.as_matrix(columns=dfA.columns[0:])
	dfB = pd.read_csv(fileB, header = None)
	dfB = dfB.as_matrix(columns=dfB.columns[0:])
	return dfA,dfB

def lassoridge(x_train,y_train,x_test,y_test,kf):
	lasso_mse=[]
	ridge_mse=[]
	for i in kf:
		mLasso = linear_model.Lasso(alpha=i)
		mRidge = linear_model.Ridge(alpha=i)
		mLasso.fit(x_train,y_train.ravel())
		mRidge.fit(x_train,y_train.ravel())
		lasso_predict = mLasso.predict(x_test)
		ridge_predict = mRidge.predict(x_test)
		lasso_mse.append(mean_squared_error(y_test.ravel(),lasso_predict))
		ridge_mse.append(mean_squared_error(y_test.ravel(),ridge_predict))
	return lasso_mse,ridge_mse	

def rmse(fileA,fileB):
	#read file
	dfA,dfB = rmseCSV(fileA,fileB)
	#10 fold cross validation
	kMse = kRetrain(dfA,dfB,10)
	x_train, x_test, y_train, y_test = train_test_split(dfA, dfB, test_size=0.10, random_state=1)
	lMse,rMse=lassoridge(x_train, x_test, y_train, y_test,kMse)
	print("Lasso")
	print("Lambda  RMSE")
	for i in range(len(kMse)):
		print(str(kMse[i])+"  "+str(lMSE[i]))
	print("Ridge")
	print("Lambda  RMSE")
	for i in range(len(kMse)):
		print(str(kMse[i])+"  "+str(rMSE[i]))
	
	


train_file = "yield.train.csv"
test_file = "yield.test.csv"
columnIDX = "Unnamed: 0"

x_train,y_train,x_test,y_test = modelCSV(train_file,test_file,columnIDX)

#Decision Tree
mdep = 6
model = modelGen(x_train, y_train, mdepth = mdep)
print("Decision Tree:")
mat_corr, cMat = predictGen(model,x_test,y_test)
#random forest
nEst = 100
mdep = None
model = modelGen(x_train, y_train,state = 1, mdepth = mdep, nEstimators = nEst)
print("Random Forest:")
 mat_corr, cMat = predictGen(model,x_test,y_test)
print(cMat)



