import todoList


def translate(event, context):
    # create a response
    if not ('id' and 'language') in event['pathParameters']:
        return {
            "statusCode": 404,
            "body": "Missing ID or language parameter"
        }
    result = todoList.translate(
        event['pathParameters']['id'], event['pathParameters']['language'])
    return {
        "statusCode": result['status_code'],
        "body": result['message']
    }
