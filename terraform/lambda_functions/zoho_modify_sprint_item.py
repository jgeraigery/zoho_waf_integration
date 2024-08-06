"""
© Copyright Kyndryl, Inc. 2024
Copyright contributors to the Zoho WAF Integration project.
This file is part of an application that is distributed under the MIT License.
Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>
"""
""" Import the modules that are required for the application"""
import os
import json
import logging
import requests
import boto3
from botocore.exceptions import ClientError

ssm = boto3.client('ssm')
lambda_client = boto3.client('lambda')
secretsmanager = boto3.client('secretsmanager')
db = boto3.resource('dynamodb')
dynamodb_table = os.getenv('DB_TABLE_NAME')
table = db.Table(dynamodb_table)
waf_update_item_function_name = os.getenv('WAF_UPDATE_ITEM_LAMBDA_NAME')
zoho_authentication_secret_name = os.getenv('ZOHO_AUTHENTICATION_SECRET_NAME')
# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_parameters():
    """Retrieve the parameters from the environment variables"""
    try:
        parameters = {
            'zoho_base_url': os.getenv('ZOHO_BASE_URL'),
            'zoho_token_url': os.getenv('ZOHO_TOKEN_URL'),
            'zoho_team_id': os.getenv('ZOHO_TEAM_ID'),
            'zoho_project_id': os.getenv('ZOHO_PROJECT_ID'),
            'zoho_sprint_id': os.getenv('ZOHO_SPRINT_ID'),
            'zoho_sprint_item_type_id': os.getenv('ZOHO_SPRINT_ITEM_TYPE_ID'),
            'zoho_risks_to_priority_mapping': os.getenv('ZOHO_RISKS_TO_PRIORITY_MAP'),
            'zoho_status_id_mapping': os.getenv('ZOHO_STATUS_ID_MAP'),
            'zoho_client_id': "",
            'zoho_client_secret': "",
            "zoho_refresh_token": ""
        }
        # Get the secrets from Secrets Manager
        secret_response = secretsmanager.get_secret_value(
            SecretId=zoho_authentication_secret_name
        )
        secret = json.loads(secret_response['SecretString'])
        # Map each secret to its value
        for key in secret:
            if key in parameters:
                parameters[key] = secret[key]
        return parameters
    except ClientError as e:
        logger.error("Error in getting parameters: %s", e)
        return None

def generate_zoho_access_token(parameters):
    """ Generate the Zoho access token"""
    try:
        # Get the Zoho token URL
        zoho_token_url = parameters['zoho_token_url']
        # Construct the Zoho token data
        zoho_token_data = {
            'refresh_token': parameters['zoho_refresh_token'],
            'client_id': parameters['zoho_client_id'],
            'client_secret': parameters['zoho_client_secret'],
            'grant_type': 'refresh_token'
        }
        # Get the Zoho access token
        token_response = requests.post(zoho_token_url, data=zoho_token_data, timeout=10)
        if token_response.status_code == 200:
            return token_response.json()['access_token']
        return None
    except ClientError as e:
        logger.error("Error in Generating Zoho Access Token: %s", e)
        return None

def check_sprint_task_status(headers, parameters, db_response):
    """ Check the status of the Zoho sprint item"""
    try:
        sprint_task_status_updates = []
        for item in db_response['Items']:
            check_sprint_item_status_url = (
                f"{parameters['zoho_base_url']}/{parameters['zoho_team_id']}/"
                f"projects/{parameters['zoho_project_id']}/"
                f"sprints/{parameters['zoho_sprint_id']}"
                f"/item/{item['itemId']}/?action=details"
            )
            check_sprint_item_status_response=requests.get(
                check_sprint_item_status_url,
                headers=headers,
                timeout=10
            )
            check_sprint_item_status_response_json = check_sprint_item_status_response.json()
            item_id = item['itemId']
            sprint_task = check_sprint_item_status_response_json["itemJObj"][item_id]
            sprint_task_priority_id = sprint_task[30]
            zoho_status_id_mapping=json.loads(parameters['zoho_status_id_mapping'])
            item_status = zoho_status_id_mapping.get(sprint_task_priority_id, "To do")
            sprint_task_status_update = {
                "QuestionId": item['QuestionId'],
                "ImprovementItem": item['ImprovementItem'],
                "itemStatus": item_status
            }
            sprint_task_status_updates.append(sprint_task_status_update)
        return sprint_task_status_updates
    except ClientError as e:
        logger.error("Error in checking Sprint Task Status: %s", e)
        return None

def update_db_table(sprint_task_status_updates):
    """ Update the database table"""
    try:
        for item in sprint_task_status_updates:
            db_update_response = table.update_item(
                        Key={
                            'QuestionId': item['QuestionId'],
                            'ImprovementItem': item['ImprovementItem']
                        },
                        UpdateExpression="set itemStatus=:st",
                        ExpressionAttributeValues={
                            ':st': item['itemStatus']
                        },
                        ReturnValues="UPDATED_NEW"
                    )
        return db_update_response
    except ClientError as e:
        logger.error("Error in updating Database: %s", e)
        return None
def lambda_handler(event, context):
    """ Lambda handler function"""
    # Get the parameters
    parameters = get_parameters()
    # Generate the Zoho access token
    zoho_access_token = generate_zoho_access_token(parameters)
    headers = {
        'Authorization': f'Bearer {zoho_access_token}'
    }

    # Get the items from DynamoDB
    db_response = table.scan()

    sprint_task_status_updates = check_sprint_task_status(
        headers,
        parameters,
        db_response
    )

    # Update DB with the sprint item status
    db_update_response = update_db_table(sprint_task_status_updates)
    if db_update_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info("Database Updated with Sprint Item Status")
        # Updating the Well Architected tool with the Sprint Item Status
        lambda_response = lambda_client.invoke(
            FunctionName=waf_update_item_function_name,
            InvocationType='Event'
        )
        logger.info("WAF Update Item Lambda Invoked: %s", lambda_response)
    else:
        logger.error("Error in updating Database with Sprint Item Status")
