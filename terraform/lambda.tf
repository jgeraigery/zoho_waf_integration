# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

# Define a lambda layer for requests module to be used in the lambda function
resource "aws_lambda_layer_version" "requests_layer" {
  filename = "${path.module}/lambda_functions/requests_layer.zip"
  layer_name = "requests_layer"
  compatible_runtimes = ["python3.9"]
}

# Zoho Create sprint item lambda afunction
resource "aws_lambda_function" "zoho_create_sprint_item" {
  function_name = "zoho_create_sprint_item"
  role          = aws_iam_role.zoho_lambda_role.arn
  handler       = "zoho_create_sprint_item.lambda_handler"
  runtime       = "python3.9"
  filename      = "${path.module}/lambda_functions/zoho_create_sprint_item.zip"
  layers        = [aws_lambda_layer_version.requests_layer.arn]
  timeout       = 60
  environment {
    variables = {
      ZOHO_TOKEN_URL              = aws_ssm_parameter.zoho_token_url.value
      ZOHO_BASE_URL               = aws_ssm_parameter.zoho_base_url.value
      ZOHO_TEAM_ID                = aws_ssm_parameter.zoho_team_id.value
      ZOHO_PROJECT_ID             = aws_ssm_parameter.zoho_project_id.value
      ZOHO_SPRINT_ID              = aws_ssm_parameter.zoho_sprint_id.value
      ZOHO_SPRINT_ITEM_TYPE_ID    = aws_ssm_parameter.zoho_sprint_item_type_id.value
      ZOHO_RISKS_TO_PRIORITY_MAP  = aws_ssm_parameter.zoho_risks_to_priority_mapping.value
      ZOHO_STATUS_ID_MAP          = aws_ssm_parameter.zoho_status_id_mapping.value
      DB_TABLE_NAME               = aws_dynamodb_table.zoho_waf_integration.name
      ZOHO_AUTHENTICATION_SECRET_NAME = aws_secretsmanager_secret.zoho_authentication.name
    }
  }
}

# WAF Create item lambda function
resource "aws_lambda_function" "waf_create_item" {
  function_name = "waf_create_item"
  role          = aws_iam_role.waf_lambda_role.arn
  handler       = "waf_create_item.lambda_handler"
  runtime       = "python3.9"
  filename      = "${path.module}/lambda_functions/waf_create_item.zip"
  timeout       = 60
  environment {
    variables = {
      DB_TABLE_NAME               = aws_dynamodb_table.zoho_waf_integration.name
      ZOHO_CREATE_ITEM_FUNCTION_NAME  = local.zoho_create_sprint_item_lambda_name
    }
  }
}

# Lambda function to update the sprint status in DynamoDB
resource "aws_lambda_function" "zoho_modify_sprint_item" {
  function_name = "zoho_modify_sprint_item"
  role          = aws_iam_role.zoho_lambda_role.arn
  handler       = "zoho_modify_sprint_item.lambda_handler"
  runtime       = "python3.9"
  filename      = "${path.module}/lambda_functions/zoho_modify_sprint_item.zip"
  layers        = [aws_lambda_layer_version.requests_layer.arn]
  timeout       = 60
  environment {
    variables = {
      ZOHO_TOKEN_URL              = aws_ssm_parameter.zoho_token_url.value
      ZOHO_BASE_URL               = aws_ssm_parameter.zoho_base_url.value
      ZOHO_TEAM_ID                = aws_ssm_parameter.zoho_team_id.value
      ZOHO_PROJECT_ID             = aws_ssm_parameter.zoho_project_id.value
      ZOHO_SPRINT_ID              = aws_ssm_parameter.zoho_sprint_id.value
      ZOHO_SPRINT_ITEM_TYPE_ID    = aws_ssm_parameter.zoho_sprint_item_type_id.value
      ZOHO_RISKS_TO_PRIORITY_MAP  = aws_ssm_parameter.zoho_risks_to_priority_mapping.value
      ZOHO_STATUS_ID_MAP          = aws_ssm_parameter.zoho_status_id_mapping.value
      DB_TABLE_NAME               = aws_dynamodb_table.zoho_waf_integration.name
      WAF_UPDATE_ITEM_LAMBDA_NAME  = local.waf_update_item_lambda_name
      ZOHO_AUTHENTICATION_SECRET_NAME = aws_secretsmanager_secret.zoho_authentication.name
    }
  }
}

# WAF Update item lambda function
resource "aws_lambda_function" "waf_update_item" {
  function_name = "waf_update_item"
  role          = aws_iam_role.waf_lambda_role.arn
  handler       = "waf_update_item.lambda_handler"
  runtime       = "python3.9"
  filename      = "${path.module}/lambda_functions/waf_update_item.zip"
  timeout       = 60
  environment {
    variables = {
      DB_TABLE_NAME               = aws_dynamodb_table.zoho_waf_integration.name
    }
  }
}