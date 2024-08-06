"""
© Copyright Kyndryl, Inc. 2024
Copyright contributors to the Zoho WAF Integration project.
This file is part of an application that is distributed under the MIT License.
Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>
"""
""" Import the modules that are required for the application"""
import os
import logging
import boto3

waf = boto3.client('wellarchitected')
db = boto3.resource('dynamodb')
dynamodb_table = os.getenv('DB_TABLE_NAME')
table = db.Table(dynamodb_table)

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """ This function is the entry point for the Lambda function"""
    # Read Item from DynamoDB
    db_response = table.scan()
    for item in db_response['Items']:
        if item['itemStatus'] == 'Done':
            waf_update_response = waf.update_answer(
                WorkloadId=item['WorkloadId'],
                LensAlias=item['LensAlias'],
                QuestionId=item['QuestionId'],
                ChoiceUpdates={
                    item['ImprovementItem']: {
                        'Status': 'SELECTED'
                    }
                }
            )
            logger.info("WAF Update Response: %s", waf_update_response)
