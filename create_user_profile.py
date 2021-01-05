import boto3
import re
from jinja2 import Template, Environment, FileSystemLoader
import sys

def lambda_handler(event, context):

    #DBからユーザを取得
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users')
    response = table.scan()
    users = response['Items']

    #一番最後に更新したユーザを取得
    users = sorted(users, key=lambda x: x['updated_at'], reverse=True)
    latest_update_user = users[0]

    #テンプレートを読み込み
    env = Environment(loader=FileSystemLoader('./jinja2_tmpl'))
    template = env.get_template('user_profile.html')

    #テンプレートをレンダーする
    data = {'user_name': latest_update_user['user_name']}
    output_text = template.render(data)  # 辞書で指定する
    print(output_text)

    #S3の情報を読み込み
    s3 = boto3.resource('s3')

    #S3のバケット名
    bucket_name = 'update-user-profile'

    #S3に置くファイル名
    key = latest_update_user['user_name'] + '/profile.html'

    #S3にファイルを置く
    output = s3.Object(bucket_name, key)
    print(output_text)
    output.put(
        ACL='public-read',
        Body=output_text,
        ContentType="text/html",
    )

#以下はlambadaで実行する時は消去
event = {
  "user_name": "koishi",
  "key2": "value2",
  "key3": "value3"
}
context = 'a'

result = lambda_handler(event, context)
