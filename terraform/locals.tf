# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

locals {
  zoho_auth_secret_arn = aws_secretsmanager_secret.zoho_authentication.arn
  zoho_waf_integration_table_arn = aws_dynamodb_table.zoho_waf_integration.arn
  zoho_create_sprint_item_lambda_arn = aws_lambda_function.zoho_create_sprint_item.arn
  zoho_create_sprint_item_lambda_name = aws_lambda_function.zoho_create_sprint_item.function_name
  zoho_modify_sprint_item_lambda_arn = aws_lambda_function.zoho_modify_sprint_item.arn
  waf_update_item_lambda_arn = aws_lambda_function.waf_update_item.arn
  waf_update_item_lambda_name = aws_lambda_function.waf_update_item.function_name
  ssm_parameter_arns = [
    aws_ssm_parameter.zoho_token_url.arn,
    aws_ssm_parameter.zoho_base_url.arn,
    aws_ssm_parameter.zoho_team_id.arn,
    aws_ssm_parameter.zoho_project_id.arn,
    aws_ssm_parameter.zoho_sprint_id.arn,
    aws_ssm_parameter.zoho_sprint_item_type_id.arn,
    aws_ssm_parameter.zoho_risks_to_priority_mapping.arn]
}