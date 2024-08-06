"""
© Copyright Kyndryl, Inc. 2024
Copyright contributors to the Zoho WAF Integration project.
This file is part of an application that is distributed under the MIT License.
Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>
"""
""" Import the modules required for the application"""
import os
import logging
import boto3
from botocore.exceptions import ClientError

waf = boto3.client('wellarchitected')
lambda_client = boto3.client('lambda')
db = boto3.resource('dynamodb')
dynamodb_table = os.getenv('DB_TABLE_NAME')
table = db.Table(dynamodb_table)
zoho_create_item_lambda_name = os.getenv('ZOHO_CREATE_ITEM_FUNCTION_NAME')

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_waf_improvement_details(workload_id, lens_alias):
    """Get the WAF improvement details"""
    try:
        result = []

        # Get the WAF Improvement summary
        waf_list_improvement_response = waf.list_lens_review_improvements(
            WorkloadId=workload_id,
            LensAlias=lens_alias,
            MaxResults=100
        )
        for summary in waf_list_improvement_response['ImprovementSummaries']:
            # Store the necessary infrmation in variables
            question_id = summary['QuestionId']
            pillar_id = summary['PillarId']
            question_title = summary['QuestionTitle']
            risk = summary['Risk']
            improvement_plan_url = summary['ImprovementPlanUrl']

            # Get the improvement items for each pillar
            waf_list_answer_response = waf.list_answers(
                WorkloadId=workload_id,
                LensAlias=lens_alias,
                PillarId=pillar_id,
                MaxResults=50,
            )

            # Iterate over the AnswerSummaries to get the Choices and ChoiceAnswerSummaries
            for pillar_question in waf_list_answer_response['AnswerSummaries']:
                if pillar_question['QuestionId'] == question_id:

                    # Get the Choices and ChoiceAnswerSummaries
                    choices = pillar_question['Choices']
                    choice_answer_summaries = pillar_question['ChoiceAnswerSummaries']

                    # Prepare sets of ChoiceIds, Answered ChoiceIds
                    choice_ids = {choice['ChoiceId'] for choice in choices}
                    answered_choice_ids = {
                        summary['ChoiceId'] for summary in choice_answer_summaries
                    }

                    # Find the unanswered ChoiceIds
                    unanswered_choice_ids = choice_ids - answered_choice_ids

                    # Remove the "None of the above" answers
                    unanswered_choice_ids = {
                        item for item in unanswered_choice_ids if not item.endswith('_no')
                    }

                    # For each unanswered ChoiceId, find its Title and Description
                    for choice_id in unanswered_choice_ids:
                        for choice in choices:
                            if choice['ChoiceId'] == choice_id:
                                title = choice['Title']
                                description = choice['Description']

                                # Construct the result
                                result.append({
                                    'WorkloadId': workload_id,
                                    'LensAlias': lens_alias,
                                    'QuestionId': question_id,
                                    'PillarId': pillar_id,
                                    'QuestionTitle': question_title,
                                    'Risk': risk,
                                    'ImprovementPlanUrl': improvement_plan_url,
                                    'ImprovementItem': choice_id,
                                    'Title': title,
                                    'Description': description
                                })
        logger.info("Succefssfully retrieved WAF improvement details")
        return result
    except ClientError as e:
        logger.error(e)
        raise e

def update_db_table(sprint_task_status_updates):
    """ Update the database table"""
    try:
        for item in sprint_task_status_updates:
            db_update_response = table.update_item(
                        Key={
                            'QuestionId': item['QuestionId'],
                            'ImprovementItem': item['ImprovementItem']
                        },
                        UpdateExpression=(
                            "SET LensAlias = :lensAlias, "
                            "PillarId = :pillarId, "
                            "QuestionTitle = :questionTitle, "
                            "Risk = :risk, "
                            "ImprovementPlanUrl = :improvementPlanUrl, "
                            "WorkloadId = :WorkloadId, "
                            "Title = :title, "
                            "Description = :description"
                        ),
                        ExpressionAttributeValues={
                            ':lensAlias': item['LensAlias'],
                            ':pillarId': item['PillarId'],
                            ':questionTitle': item['QuestionTitle'],
                            ':risk': item['Risk'],
                            ':improvementPlanUrl': item['ImprovementPlanUrl'],
                            ':WorkloadId': item['WorkloadId'],
                            ':title': item['Title'],
                            ':description': item['Description']
                        },
                        ReturnValues="UPDATED_NEW"
                    )
        return db_update_response
    except ClientError as e:
        logger.error("Error in updating Database: %s", e)
        return None

def lambda_handler(event, context):
    """ This function is the entry point for the Lambda function"""
    workload_id = event['detail']['requestParameters']['WorkloadId']
    lens_alias = event['detail']['responseElements']['LensAlias']
    logger.info("WorkloadId : %s", workload_id)
    logger.info("lens_alias : %s", lens_alias)
    waf_improvement_results = get_waf_improvement_details(workload_id, lens_alias)

    # Store the result in DynamoDB
    if waf_improvement_results:
        for item in waf_improvement_results:
            logger.info("Adding item to DynamoDB: %s", item)
            # table.put_item(Item=item)
            update_db_table([item])
    # Invoke the Zoho update sprint item lambda function
    lambda_response = lambda_client.invoke(
        FunctionName=zoho_create_item_lambda_name,
        InvocationType='Event'
    )
    logger.info("Zoho Create Sprint Item Lambda Invoked: %s",lambda_response)
