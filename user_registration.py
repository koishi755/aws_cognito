import json
import boto3
import urllib
import datetime


#DBから一番新しいユーザIDを取得
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')
response = table.scan()
users = response['Items']
users = sorted(users, key=lambda x: x['user_id'], reverse=True)
latest_user_id = users[0]['user_id']

user_name = "test4"
password = "Test111-"
email = 'test@koishi.com'

def register():

    for user in users:
        registered_user_name = user['user_name']
        if user_name in registered_user_name :
            return '既に登録されているユーザーです。'

    #今回登録するユーザーID
    register_id = latest_user_id + 1

    #更新日時を取得
    updated_at = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    updated_at = int(updated_at)

    #DynamoDBにユーザーを登録
    table.put_item(
        Item={
            'user_id': register_id,
            'updated_at': updated_at,
            'user_name': user_name,
            'password': password,
            'email': email
        }
    )
    return 'ユーザー登録に成功しました'

result = register()
