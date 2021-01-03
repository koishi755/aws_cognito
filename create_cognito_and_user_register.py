import json
import boto3
import random
import string
import datetime

#DBからユーザ一覧を取得
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')
response = table.scan()
users = response['Items']

#1番新しいユーザIDを取得
users = sorted(users, key=lambda x: x['user_id'], reverse=True)
latest_user_id = users[0]['user_id']
user_id = latest_user_id + 1

def lambda_handler(event, context):
    # TODO implement
    result = register(event)
    print(result)
    if result == False :
        return '既に登録されているユーザー名です。'
        
    create_cognito(event)
    return 'ユーザー登録に成功しました。'

def register(event):

    #登録するユーザー名など
    user_name = event['user_name']
    password = event['password']
    email = event['email']
    
    # DBに同じユーザー名がいないか確認
    for user in users:
        registered_user_name = user['user_name']
        if user_name in registered_user_name:
            return False

    #今回登録するユーザーID
    user_id = latest_user_id + 1

    #更新日時を取得
    updated_at = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    updated_at = int(updated_at)

    table.put_item(
        Item={
            'user_id': user_id,
            'updated_at': updated_at,
            'user_name': user_name,
            'email': email
        }
    )
    return True

def create_cognito(event):
    
    #登録するユーザー名など
    user_name = event['user_name']
    password = event['password']
    email = event['email']
    

    #ランダムなドメインを生成
    dat = string.digits + string.ascii_lowercase
    domain = ''.join([random.choice(dat) for i in range(10)])

    #各ユーザのページ
    user_profile_url = 'https://update-user-profile.s3-ap-northeast-1.amazonaws.com/{}.html'
    user_profile_url = user_profile_url.format(user_name)

    #お約束
    client = boto3.client('cognito-idp')

    #cognito ユーザープール作成
    response = client.create_user_pool(
        PoolName=user_name,
    )

    #ユーザープールのみ取り出し
    user_pool = response['UserPool']

    #プールIDを取得
    user_pool_id = user_pool['Id']

    #アプリクライアントを作成
    response = client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=user_name,
        GenerateSecret=False,
        RefreshTokenValidity=30,
        ReadAttributes=[
            'address',
            'birthdate',
            'email',
            'email_verified',
            'family_name',
            'gender',
            'given_name',
            'locale',
            'middle_name',
            'name',
            'nickname',
            'phone_number',
            'phone_number_verified',
            'picture',
            'preferred_username',
            'profile',
            'updated_at',
            'website',
            'zoneinfo'
        ],
        WriteAttributes=[
            'address',
            'birthdate',
            'email',
            'family_name',
            'gender',
            'given_name',
            'locale',
            'middle_name',
            'name',
            'nickname',
            'phone_number',
            'picture',
            'preferred_username',
            'profile',
            'updated_at',
            'website',
            'zoneinfo'
        ],
        ExplicitAuthFlows=[
            'ALLOW_CUSTOM_AUTH',
            'ALLOW_REFRESH_TOKEN_AUTH',
            'ALLOW_USER_SRP_AUTH'
        ],
        SupportedIdentityProviders=[
            'COGNITO',
        ],
        CallbackURLs=[
            user_profile_url
        ],
        AllowedOAuthFlows=[
            'code',
            'implicit'
        ],
        AllowedOAuthScopes=[
            'aws.cognito.signin.user.admin',
            'email',
            'openid',
            'phone',
            'profile'
        ],
        AllowedOAuthFlowsUserPoolClient=True,
        PreventUserExistenceErrors='ENABLED'
    )

    #クライアントIDを取得
    client_id = response['UserPoolClient']['ClientId']

    #ドメインを作成
    response = client.create_user_pool_domain(
        Domain=domain,
        UserPoolId=user_pool_id,
    )

    #ログインURLを定義
    login_url = {
        'https': 'https://{}.auth.ap-northeast-1.amazoncognito.com/'.format(domain),
        'login': 'login?client_id={}&'.format(client_id),
        'response_type': 'response_type=token&scope=aws.cognito.signin.user.admin+email+openid+phone+profile&',
        'redirect_uri': 'redirect_uri=https://update-user-profile.s3-ap-northeast-1.amazonaws.com/{}.html'.format(user_name)
    }

    #ログインURLを作成
    url = ''
    for v in login_url.values():
        url = url + v

    #クライアントユーザを作成
    response = client.sign_up(
        ClientId=client_id,
        Username=user_name,
        Password=password,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            }
        ]
    )

    #ユーザをユーザプールに参加
    response = client.admin_confirm_sign_up(
        UserPoolId=user_pool_id,
        Username=user_name
    )

    #DBにURLを登録
    response = table.update_item(
        Key={
            'user_id': user_id
        },
        UpdateExpression='set user_url = :url',
        ExpressionAttributeValues={
            ":url": url
        }
    )

