from flask import Flask, render_template, request
import boto3

client = boto3.client('dynamodb')
resource = boto3.resource('dynamodb')
table_name = 'donar'
donar_table = resource.Table('donar')
recipient_table = resource.Table('recipient')

id = 0

table = resource.Table(table_name)

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

# id+=1
# details['id'] = id
# details['name'] = str(request.form['name'])
# details['age'] = str(request.form['age'])
# details['address'] = str(request.form['address'])
# details['contact'] = str(request.form['contact'])
# details['medical_history'] = str(request.form['medical_history'])
# details['blood_group'] = str(request.form['blood_group'])
# details['organ'] = str(request.form['organ'])





donar_response = donar_table.scan()
recipient_response = recipient_table.scan()

donars = donar_response['Items']
recipient = recipient_response['Items']

# while 'LastEvaluatedKey' in donar_response:
#     donar_response = donar_table.scan(ExclusiveStartKey=donar_response['LastEvaluatedKey'])
#     donar_items.extend(donar_response['Items'])

# while 'LastEvaluatedKey' in recipient_response:
#     recipient_response = recipient_table.scan(ExclusiveStartKey=recipient_response['LastEvaluatedKey'])
#     recipient_items.extend(recipient_response['Items'])


index = []
for i in range(len(donars)):
    if donars[i]['organ'].lower() == recipient[0]['organ'].lower():
        index.append(i)

for i in index:
    print(donars[i])

# print(donar_items)
# print(recipient_items)
