import boto3
from string import digits
import re
from flask import Flask, render_template, request
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.naive_bayes import BernoulliNB
nltk.download('stopwords')
nltk.download('wordnet')


# Initialize Flask app
app = Flask(__name__)


session = boto3.Session(region_name='ap-south-1')

client = session.client('dynamodb')
resource = session.resource('dynamodb')

# Define the route for the loan prediction form

id = 0

@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/predict')
def loan_prediction_form():
    return render_template('predict.html')


@app.route('/donate')
def donation():
    return render_template('donate.html')


@app.route('/recieve')
def receive():
    return render_template('recieve.html')

# Define the route for receiving form data and returning prediction


@app.route('/predict', methods=['POST'])
def predict():
    # Get form data

    input = str(request.form['input'])
    # reading the csv file
    training_df = pd.read_csv('Training.csv')
    
    # splitting into predictors and response
    X_train = training_df.drop(columns=['prognosis'])
    y_train = training_df['prognosis']
    X_train = X_train.iloc[:,:-1]

    column_names = list(X_train.columns.values)
    split_list = [word.split('_') for word in column_names]

    lemmatizer = WordNetLemmatizer()

    lemmatized_list = [[lemmatizer.lemmatize(word) for word in sublist  if word not in set(stopwords.words('english'))] for sublist in split_list]

    joined_list = ['_'.join(word) for word in lemmatized_list]

    X_train = X_train.rename(columns=dict(zip(X_train.columns, joined_list)))

    # creating an instance of BernoulliNB
    clf = BernoulliNB()
    # training the model
    clf.fit(X_train,y_train)

    # ----- Performing preprocessing on dataset ------
    #converting it to lowercase
    input = input.lower()
    # removing numbers
    remove_digits = input.maketrans('', '', digits)
    input = input.translate(remove_digits)
    # REPLACING NEXT LINES BY 'WHITE SPACE'
    input = input.replace(r'\n', " ")
    # REPLACING CURRENCY SIGNS BY 'MONEY'
    input = input.replace(r'Â£|\$', 'Money')
    # REPLACING SPECIAL CHARACTERS BY WHITE SPACE
    input = re.sub('[^A-Za-z0-9]+', ' ', input)
    # REPLACING LARGE WHITE SPACE BY SINGLE WHITE SPACE
    input = input.replace(r'\s+', ' ')
    # tokenizing the input and converting it to set
    tokens = input.split(' ')

    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in set(stopwords.words('english'))]

    tokens = set(tokens)

    columns = X_train.columns
    test_vec = []
    for c in columns:
        col_vec = c.split('_')
        if len(col_vec)==1:
            if col_vec[0] in tokens:
                test_vec.append(1)
            else: 
                test_vec.append(0)
        else:
            count = 0
            for temp in col_vec:
                if temp in tokens:
                    count = count + 1
                    
            if count == len(col_vec):
                test_vec.append(1)
            else:
                test_vec.append(0)
                
    
    prediction = clf.predict([test_vec])[0]
    
    return render_template('predict.html',prediction=prediction)


@app.route('/donate', methods=['POST'])
def donar_entry():

    client = boto3.client('dynamodb')
    resource = boto3.resource('dynamodb')

    donar_table = resource.Table('donar')
    recipient_table = resource.Table('recipient')

    table = resource.Table('donar')

    details = {
        'id': 0,
        'name': '',
        'age': 0,
        'address': '',
        'contact': '',
        'medical_history': '',
        'blood_group': '',
        'organ': ''
    }

    global id
    id += 1
    details['id'] = id
    details['name'] = str(request.form['name'])
    details['age'] = str(request.form['age'])
    details['address'] = str(request.form['address'])
    details['contact'] = str(request.form['contact'])
    details['medical_history'] = str(request.form['medical_history'])
    details['blood_group'] = str(request.form['blood_group'])
    details['organ'] = str(request.form['organ'])

    response = table.put_item(Item=details)

    return render_template('donate.html')

@app.route('/recieve', methods=['POST'])
def recieve():

    table = resource.Table('recipient')

    details = {
        'id': 0,
        'name': '',
        'age': 0,
        'address': '',
        'contact': '',
        'medical_history': '',
        'blood_group': '',
        'organ': ''
    }

    details['id'] = id
    details['name'] = str(request.form['name'])
    details['age'] = str(request.form['age'])
    details['address'] = str(request.form['address'])
    details['contact'] = str(request.form['contact'])
    details['medical_history'] = str(request.form['medical_history'])
    details['blood_group'] = str(request.form['blood_group'])
    details['organ'] = str(request.form['organ'])

    response = table.put_item(Item=details)

    donar_table = resource.Table('donar')
    recipient_table = resource.Table('recipient')

    donar_response = donar_table.scan()
    recipient_response = recipient_table.scan()

    donars = donar_response['Items']
    recipient = recipient_response['Items']

    index = []
    for i in range(len(donars)):
        if donars[i]['organ'].lower() == recipient[0]['organ'].lower():
            index.append(i)

    for i in index:
        print("Matched")
        print(donars[i])
    
    
    result = ""
    if len(donars)==0:
        result = "No Angel Found"
    else:
        result = f'''
            We have found an angel named : {donars[0]['name']}
            Contact: {donars[0]['contact']}
            Medical history: {donars[0]['medical_history']}
            Address: {donars[0]['address']}
            Age: {donars[0]['age']}

        '''
        

    return render_template('recieve.html',result=result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
