
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.ensemble import VotingClassifier
import sklearn as sk
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
#Model from SciKit-Learn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn import feature_selection
from sklearn.impute import SimpleImputer

# Model Evaluations from SciKit Learn
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix,precision_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import precision_score


# Create your views here.
from Remote_User.models import ClientRegister_Model,Prediction_Results,detection_ratio,detection_accuracy,Job_Post_Prediction


def serviceproviderlogin(request):
    if request.method  == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password =="Admin":
            detection_accuracy.objects.all().delete()
            return redirect('View_Remote_Users')

    return render(request,'SProvider/serviceproviderlogin.html')

def Find_Predict_Jop_Post_Type_Details_Ratio(request):
    detection_ratio.objects.all().delete()
    ratio = ""
    kword = 'Real'
    print(kword)
    obj = Job_Post_Prediction.objects.all().filter(Q(Prediction_Details=kword))
    obj1 = Job_Post_Prediction.objects.all()
    count = obj.count();
    count1 = obj1.count();
    ratio = (count / count1) * 100
    if ratio != 0:
        detection_ratio.objects.create(names=kword, ratio=ratio)

    ratio1 = ""
    kword1 = 'Fake'
    print(kword1)
    obj1 = Job_Post_Prediction.objects.all().filter(Q(Prediction_Details=kword1))
    obj11 = Job_Post_Prediction.objects.all()
    count1 = obj1.count();
    count11 = obj11.count();
    ratio1 = (count1 / count11) * 100
    if ratio1 != 0:
        detection_ratio.objects.create(names=kword1, ratio=ratio1)

    obj = detection_ratio.objects.all()
    return render(request, 'SProvider/Find_Predict_Jop_Post_Type_Details_Ratio.html', {'objs': obj})

def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

def ViewTrendings(request):
    topic = Prediction_Results.objects.values('topics').annotate(dcount=Count('topics')).order_by('-dcount')
    return  render(request,'SProvider/ViewTrendings.html',{'objects':topic})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def Predict_Jop_Post_Type_Details(request):


    obj1 = Prediction_Results.objects.values('Job_Id',
    'Actual_Fake',
    'Predicted_Fake')

    Job_Post_Prediction.objects.all().delete()
    for t in obj1:

        Job_Id= t['Job_Id']
        Actual_Fake= t['Actual_Fake']
        Predicted_Fake= t['Predicted_Fake']
        if( Predicted_Fake == "Predicted Fake"):
            Predicted_Fake='0'
        try :
            Predicted_Fake1=int(Predicted_Fake)
        except:
            Predicted_Fake1=0

        if Predicted_Fake1 == 0:
            predict = 'Real'
        else:
            predict = 'Fake'

        Job_Post_Prediction.objects.create(Job_Id=Job_Id,
        Actual_Fake=Actual_Fake,
        Predicted_Fake=Predicted_Fake,
        Prediction_Details=predict)

    obj = Job_Post_Prediction.objects.all()

    return render(request, 'SProvider/Predict_Jop_Post_Type_Details.html', {'list_objects': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Trained_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="TrainedData.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = Job_Post_Prediction.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:
        row_num = row_num + 1
        ws.write(row_num, 0, my_row.Job_Id, font_style)
        ws.write(row_num, 1, my_row.Actual_Fake, font_style)
        ws.write(row_num, 2, my_row.Predicted_Fake, font_style)
        ws.write(row_num, 3, my_row.Prediction_Details, font_style)

    wb.save(response)
    return response

def train_model(request):
    detection_accuracy.objects.all().delete()

    # for displaying graph in the notebook
    # load data
    df_job = pd.read_csv('Job_Posting_DataSets.csv',encoding='latin1')
    df_job.head(2)
    # Calculating NUll data
    df_job.isna().sum()
    # reviewing data structure
    df_job.dtypes
    # Filling the Categorical values with 'missing'
    data_cat_imp = SimpleImputer(strategy="constant", fill_value="Missing")
    cat_imp_feature = ["title", "location", "department", "salary_range", "company_profile", "description",
                       "requirements", "benefits",
                       "employment_type", "required_experience", "required_education", "industry", "function"]

    # Filling the Numerical values through existing value
    data_num_imp = SimpleImputer(strategy="constant", fill_value=None)
    num_imp_feature = ["job_id", "telecommuting", "has_company_logo", "has_questions", "fraudulent"]

    # Transforming into column
    data_imp_trans = ColumnTransformer([("data_cat_imp", data_cat_imp, cat_imp_feature),
                                        ("data_num_imp", data_num_imp, num_imp_feature)])

    # Transforming and assigning the data
    transformed_data = data_imp_trans.fit_transform(df_job)
    transformed_data
    # Transforming the data into data frame
    df_job_transformed_data = pd.DataFrame(transformed_data,
                                           columns=["title", "location", "department", "salary_range",
                                                    "company_profile", "description",
                                                    "requirements", "benefits", "employment_type",
                                                    "required_experience", "required_education",
                                                    "industry", "function", "job_id", "telecommuting",
                                                    "has_company_logo", "has_questions",
                                                    "fraudulent"])
    # viewing transformed data
    df_job_transformed_data.head(2)
    # verify the NaN/missing values
    df_job_transformed_data.isna().sum()
    # reviewing the columns
    df_job_transformed_data.columns
    # random seed
    np.random.seed(42)

    # data split into feature(X) and label(y)
    X_trans = df_job_transformed_data.drop("fraudulent", axis=1)
    y_trans = df_job_transformed_data.fraudulent
    y_trans = y_trans.astype('int')

    print("X Trans")
    print(X_trans)
    print("Y Trans")
    print(y_trans)

    # shape(row,column) of features and label
    X_trans.shape, y_trans.shape, X_trans.columns
    # Instantation of One Hot Encoder for categorical data tarnsformatio into Numeric
    one_hot = OneHotEncoder()
    clf_trans = ColumnTransformer([("one_hot", one_hot, cat_imp_feature)], remainder="passthrough")
    X_trans_fin = clf_trans.fit_transform(X_trans)
    np.array(X_trans_fin)
    # splitting the data into train and test with 23% reserved for testing and 77% for training
    X_train, X_test, y_train, y_test = train_test_split(X_trans_fin, y_trans, test_size=0.23, random_state=42)
    X_train.shape, X_test.shape, y_train.shape, y_test.shape
    # Lets fit the model
    np.random.seed(42)

    models = []
    # RandomForestClassifier

    # Applying Random Forest Classifier Model
    model_rfm = RandomForestClassifier()
    # fitting the data into model
    model_rfm.fit(X_train, y_train, sample_weight=None)
    # scoring the Random Forest Classifier Model
    print("Fake Job Random Forest Model Accuracy : {model_rfm.score(X_test,y_test)*100:.2f}%")
    # predicting label data through Random Forest Classifier Model
    y_pred_rfm = model_rfm.predict(X_test)
    y_pred_rfm

    # LogisticRegression
    print("Logistic Regression")
    # Applying Logistic Regression Classification Algorithm
    model_lrm = LogisticRegression(solver='liblinear')
    # fitting the data into model
    model_lrm.fit(X_train, y_train, sample_weight=None)
    # scoring the Logistic Regression Model
    print("Fake Job Logistic Regression Model Accuracy :{model_lrm.score(X_test,y_test)*100:.2f}%")
    # predicting label data through Random Forest Classifier Model
    y_pred_lrm = model_lrm.predict(X_test)
    y_pred_lrm
    model_lrm.get_params()
    # accuracy metrics of Random forest

    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred_lrm))
    print("Accuracy Score ~ :{accuracy_score(y_test,y_pred_rfm)*100:.2f}%")
    # precision score of Random forest
    print("Precision Score~ :{precision_score(y_test,y_pred_rfm)*100:.2f}%")
    # classification report
    print(classification_report(y_test, y_pred_rfm))
    # Confusion Matrix - It's compare to the label model predict and the actual label it suppossed to predict,
    # its offer an ideal where the model is getting confused.

    detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test,y_pred_rfm)*100)

    # SVM Model
    print("SVM")
    from sklearn import svm
    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print("SVM ACCURACY")
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    models.append(('svm', lin_clf))

    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

    print("Naive Bayes")

    from sklearn.naive_bayes import MultinomialNB
    NB = MultinomialNB()
    NB.fit(X_train, y_train)
    predict_nb = NB.predict(X_test)
    naivebayes = accuracy_score(y_test, predict_nb) * 100
    print(naivebayes)
    print(confusion_matrix(y_test, predict_nb))
    print(classification_report(y_test, predict_nb))
    models.append(('naive_bayes', NB))

    detection_accuracy.objects.create(names="Naive Bayes", ratio=naivebayes)

    print("RandomForestClassifier")

    rfm_data = confusion_matrix(y_test, y_pred_rfm)
    sns.set(font_scale=1)
    #sns.heatmap(rfm_data, center=0, annot=True, cmap="YlGnBu");
    plt.xlabel("Actual Label")
    plt.ylabel("Predicted Label");
    # accuracy metrics of logistic
    print("Accuracy Score ~ :{accuracy_score(y_test,y_pred_lrm)*100:.2f}%")
    # precision score of logistic
    print("Precision Score~ :{precision_score(y_test,y_pred_lrm)*100:.2f}%")
    # classification report
    print(classification_report(y_test, y_pred_lrm))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred_rfm))
    # Confusion Matrix - It's compare to the label model predict and the actual label it suppossed to predict,
    # its offer an ideal where the model is getting confused.

    detection_accuracy.objects.create(names="Random Forest Classifier", ratio=accuracy_score(y_test,y_pred_lrm)*100)

    lrm_data = confusion_matrix(y_test, y_pred_lrm)
    sns.set(font_scale=1)
    sns.heatmap(lrm_data, center=0, annot=True, cmap="YlOrBr");
    plt.xlabel("Actual Label")
    plt.ylabel("Predicted Label");
    # optimal parameters using LogisticRegression() for classification
    random_grid = {"C": np.logspace(-4, 4, 20),
                   "solver": ["liblinear"]
                   }

    # displaying the random grid parameters for the estimator ~ Logistic Regression
    random_grid

    # Use the random grid to search for optomised hyperparameters for LogisticRegression()
    rf = LogisticRegression()

    # Random search of parameters, using 3 fold cross validation,and search across 2 different combinations
    rf_random = RandomizedSearchCV(estimator=rf, param_distributions=random_grid,
                                   n_iter=10, cv=3, verbose=True)

    # Fitting the RandomizedSearchCV model
    rf_random.fit(X_train, y_train)
    # Optimised parameters
    rf_random.best_params_
    # fitting the LogisticRegression() model with optimsed parameters
    model_lrm_ideal = LogisticRegression(C=545.5594781168514,
                                         solver='liblinear',
                                         verbose=True)
    # fitting the model
    model_lrm_ideal.fit(X_train, y_train)
    # scoring the ideal LogisticRegression() Model
    model_lrm_ideal.score(X_test, y_test)
    # predicting data through LogisticRegression() Model
    y_pred_lrm_ideal = model_lrm_ideal.predict(X_test)
    y_pred_lrm_ideal
    # accuracy score of post optimization of LogisticRegression() Model
    print("Accuracy Score~ :{accuracy_score(y_test,y_pred_lrm_ideal)*100:.2f}%")
    # formatting in the desired format
    df_job_pred = pd.DataFrame()
    df_job_pred["Actual Fake"] = y_test
    df_job_pred["Predicted Fake"] = y_pred_rfm
    df_job_pred.to_excel("predictions.xlsx")

    #df_job_pred.to_csv("predictions.csv")
    df_job_pred.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request,'SProvider/train_model.html', {'objs': obj})














