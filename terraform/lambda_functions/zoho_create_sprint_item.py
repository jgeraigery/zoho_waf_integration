"""
© Copyright Kyndryl, Inc. 2024
Copyright contributors to the Zoho WAF Integration project.
This file is part of an application that is distributed under the MIT License.
Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>
"""
""" Import the modules required for the application"""
import os
import json
import logging
import requests
import boto3
from botocore.exceptions import ClientError

ssm = boto3.client('ssm')
secretsmanager = boto3.client('secretsmanager')
db = boto3.resource('dynamodb')
dynamodb_table = os.getenv('DB_TABLE_NAME')
table = db.Table(dynamodb_table)
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

def create_zoho_sprint_item(item, headers, parameters, sprint_task_data):
    """ Create the Zoho sprint item"""
    try:
        risk=item['dynamodb']['NewImage']['Risk']['S']
        title=item['dynamodb']['NewImage']['Title']['S']
        question_title=item['dynamodb']['NewImage']['QuestionTitle']['S']
        description=item['dynamodb']['NewImage']['Description']['S']
        improvement_url=item['dynamodb']['NewImage']['ImprovementPlanUrl']['S']
        question_id=item['dynamodb']['NewImage']['QuestionId']['S']
        improvement_item=item['dynamodb']['NewImage']['ImprovementItem']['S']
        # Create the title for the sprint task
        sprint_task_data['name'] = "WAF " + risk + " risk item: " + title

        # Create the description for the sprint task
        sprint_task_data['description'] = (
            "<b>Well Architected Framework Action</b><br>" +
            "<b>Question:</b> " + question_title + "<br>" +
            "<b>Risk Item:</b> " + title + "<br>" +
            "<b>Description:</b> " + description + "<br>" +
            "<b>Improvement Plan:</b> <a href=" + improvement_url +
            'target="_blank">Improvement Plan Link</a>'
        )

        # Decide the sprint task priority. If none available set to default 28933000000008214(LOW)
        sprint_task_data['projpriorityid'] = json.loads(
            parameters[
                'zoho_risks_to_priority_mapping'
            ]).get(
                risk,
                "28933000000008214"
            )

        # Get the sprint item id from the database. If not available set to None
        sprint_item_id = item.get('itemId', None)

        # Generate Sprint task url
        create_sprint_task_url = (
            f"{parameters['zoho_base_url']}/{parameters['zoho_team_id']}/"
            f"projects/{parameters['zoho_project_id']}/"
            f"sprints/{parameters['zoho_sprint_id']}/item/"
        )

        # Check if the sprint task is already created
        if sprint_item_id is not None and sprint_item_id != "":
            logger.info("Sprint Item: %s already exists", sprint_item_id)
        else:
            # Create sprint item
            sprint_task_response = requests.post(
                create_sprint_task_url,
                headers=headers,
                data=sprint_task_data,
                timeout=10
            )
            if sprint_task_response.json()['status'] == "success":
                combined_response = sprint_task_response.json()
                combined_response.update(
                    {
                        "QuestionId": question_id,
                        "ImprovementItem": improvement_item,
                        "SprintId": parameters['zoho_sprint_id'],
                    }
                )
                logger.info("Sprint Item: %s created successfully", combined_response['itemNo'])
                return combined_response
            logger.error("Error in Creating Zoho Sprint Item: %s", sprint_task_response.json())
        return None
    except ClientError as e:
        logger.error("Error in Creating Zoho Sprint Item: %s", e)
        return None

def update_db_table(item):
    """ Update the database table"""
    try:
        db_update_response = table.update_item(
                Key={
                    'QuestionId': item['QuestionId'],
                    'ImprovementItem': item['ImprovementItem']
                },
                UpdateExpression="set sprintId = :s, itemId = :i, itemNo = :n, itemStatus=:st",
                ExpressionAttributeValues={
                    ':s': item['SprintId'],
                    ':i': item['addedItemId'],
                    ':n': item['itemNo'],
                    ':st': 'To do'
                },
                ReturnValues="UPDATED_NEW"
            )
        # Check the response from the database if Attributes ->HTTPStatusCode is 200
        if db_update_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.info("Database Updated with Sprint Item: %s", item['itemNo'])
    except ClientError as e:
        logger.error("Error in updating Database: %s", e)
        return None
def lambda_handler(event, context):
    """ Lambda handler function"""
    logger.info(event)
    # Get the parameters
    parameters = get_parameters()
    # Generate the Zoho access token
    zoho_access_token = generate_zoho_access_token(parameters)
    headers = {
        'Authorization': f'Bearer {zoho_access_token}'
    }
    sprint_task_data = {}
    sprint_task_responses = []
    sprint_task_data['projitemtypeid'] = parameters['zoho_sprint_item_type_id']
    for item in event['Records']:
        if item['eventName'] == 'INSERT':
            create_zoho_sprint_item_response=create_zoho_sprint_item(
                item,
                headers,
                parameters,
                sprint_task_data
            )
            if create_zoho_sprint_item_response and 'status' in create_zoho_sprint_item_response:
                if create_zoho_sprint_item_response['status'] == "success":
                    sprint_task_responses.append(create_zoho_sprint_item_response)

    # # Update database entry with the sprint item id
    for item in sprint_task_responses:
        update_db_table(item)
