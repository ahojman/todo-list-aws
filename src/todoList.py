import os
import boto3
import time
import uuid
import json
import functools
from botocore.exceptions import ClientError


def get_table(dynamodb=None):
    # The ‘not’ is a Logical operator in Python that will
    #   return True if the expression is False.
    if not dynamodb:
        URL = os.environ['ENDPOINT_OVERRIDE']
        if URL:
            print('URL dynamoDB:'+URL)
            boto3.client = functools.partial(boto3.client, endpoint_url=URL)
            boto3.resource = functools.partial(boto3.resource,
                                               endpoint_url=URL)
        dynamodb = boto3.resource("dynamodb")
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#service-resource
    # fetch todo from the database
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    return table


def get_item(key, dynamodb=None):
    # captures the Table returned by this method.
    table = get_table(dynamodb)
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.get_item
    try:
        result = table.get_item(
            Key={
                'id': key
            }
        )
    # this one comes from botocore.exceptions
    # and will raise an error and print the Error Message
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Result getItem:'+str(result))
        if 'Item' in result:
            return result['Item']


def get_items(dynamodb=None):
    table = get_table(dynamodb)
    # fetch todo from the database
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.scan
    result = table.scan()
    return result['Items']


def put_item(text, dynamodb=None):
    table = get_table(dynamodb)
    timestamp = str(time.time())
    print('Table name:' + table.name)
    item = {
        'id': str(uuid.uuid1()),
        'text': text,
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }
    try:
        # write the todo to the database
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.put_item
        table.put_item(Item=item)
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(item)
        }
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


def update_item(key, text, checked, dynamodb=None):
    table = get_table(dynamodb)
    timestamp = int(time.time() * 1000)
    # update the todo in the database
    try:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.update_item
        result = table.update_item(
            Key={
                'id': key
            },
            ExpressionAttributeNames={
              '#todo_text': 'text',
            },
            ExpressionAttributeValues={
              ':text': text,
              ':checked': checked,
              ':updatedAt': timestamp,
            },
            UpdateExpression='SET #todo_text = :text, '
                             'checked = :checked, '
                             'updatedAt = :updatedAt',
            ReturnValues='ALL_NEW',
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return result['Attributes']


def delete_item(key, dynamodb=None):
    table = get_table(dynamodb)
    # delete the todo from the database
    try:
        table.delete_item(
            Key={
                'id': key
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return


def translate(key, lang):
    item = get_item(key)
    try:
        if not item:
            return {"status_code": 404, "message": f"Id {key} not present"}
        translate = boto3.client('translate')
        result = translate.translate_text(Text=item['text'],
                                          SourceLanguageCode="auto",
                                          TargetLanguageCode=lang)
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {"status_code": 422, "message": e.response['Error']['Message']}
    else:
        return {"status_code": 200, "message": result.get('TranslatedText')}


def create_todo_table(dynamodb):
    # For unit testing
    tableName = os.environ['DYNAMODB_TABLE']
    print('Creating Table with name:' + tableName)
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.table_status
    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
    if (table.table_status != 'ACTIVE'):
        raise AssertionError()
    return table
