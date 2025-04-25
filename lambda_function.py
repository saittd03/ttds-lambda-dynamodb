import json
import boto3
from urllib.parse import parse_qs, unquote

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ttdseva')  # Make sure this table exists

def lambda_handler(event, context):
    try:
        mypage = page_router(event['httpMethod'], event.get('queryStringParameters'), event.get('body'))
        return mypage
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def page_router(httpmethod, querystring, formbody):
    if httpmethod == 'GET':
        return serve_html('index.html')

    elif httpmethod == 'POST':
        try:
            insert_record(formbody)
            return serve_html('success.html')
        except Exception as e:
            return error_response(e)

    elif httpmethod == 'DELETE':
        if querystring and 'aadhar' in querystring:
            return delete_record(querystring['aadhar'][0])  # Accessing the first item in the list
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Aadhar number required for deletion'})
            }

def serve_html(filename):
    try:
        with open(filename, 'r') as htmlFile:
            htmlContent = htmlFile.read()
        return {
            'statusCode': 200,
            'headers': {"Content-Type": "text/html"},
            'body': htmlContent
        }
    except Exception as e:
        return error_response(e)

def error_response(e):
    return {
        'statusCode': 500,
        'body': json.dumps({'error': str(e)})
    }

def insert_record(formbody):
    # Decode URL-encoded form data and convert to dictionary
    formbody = unquote(formbody)
    data = parse_qs(formbody)

    # Print the parsed data for debugging
    print("Parsed data:", data)

    # Ensure 'aadharnumber' is present
    if 'aadhar' not in data:
        raise ValueError('Aadhar number is required')

    # Prepare the item for insertion (ensure all required fields are included)
    item = {k: v[0] for k, v in data.items()}  # Extracting first value of each key-value pair

    # Ensure 'aadharnumber' is part of the item before inserting
    if 'aadhar' in item:
        item['aadharnumber'] = item.pop('aadhar')  # Rename 'aadhar' to 'aadharnumber'

    print("Item to insert:", item)

    # Put item into DynamoDB
    table.put_item(Item=item)
    return {"message": "Record inserted successfully"}

def delete_record(aadhar_number):
    try:
        response = table.delete_item(
            Key={
                'aadharnumber': aadhar_number  # Use the correct partition key here
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Record deleted successfully', 'response': response})
        }
    except Exception as e:
        return error_response(e)
