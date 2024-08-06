# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

# Create an event bridge rule that captures the wellarchitected events
resource "aws_cloudwatch_event_rule" "wellarchitected_rule" {
    name        = "wellarchitected_rule"
    description = "Rule to capture wellarchitected Update answer events"
    event_pattern = jsonencode({
        source: ["aws.wellarchitected"],
        region: [var.aws_region],
        detail: {
            eventName: ["UpdateAnswer"]
        }
    })
}
# Create a target for the event bridge rule
resource "aws_cloudwatch_event_target" "wellarchitected_target" {
  rule      = aws_cloudwatch_event_rule.wellarchitected_rule.name
  target_id = "wellarchitected_target"
  arn       = aws_lambda_function.waf_create_item.arn
}

resource "aws_lambda_permission" "allow_event_bridge_to_invoke_lambda" {
    statement_id  = "AllowExecutionFromEventBridge"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.waf_create_item.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.wellarchitected_rule.arn
}

# A schedule rule for the lambda function
resource "aws_cloudwatch_event_rule" "zoho_check_sprint_status_rule" {
    name        = "zoho_check_sprint_status_rule"
    description = "Rule to trigger lambda function every 5 minutes"
    schedule_expression = "rate(5 minutes)"
}

# The rule will trigger a lambda function.
resource "aws_cloudwatch_event_target" "zoho_check_sprint_status_target" {
  rule      = aws_cloudwatch_event_rule.zoho_check_sprint_status_rule.name
  target_id = "zoho_check_sprint_status_target"
  arn       = aws_lambda_function.zoho_modify_sprint_item.arn
}

# Permission to the lambda function to allow the event bridge to invoke it
resource "aws_lambda_permission" "allow_event_bridge_to_invoke_zoho_update_lambda" {
    statement_id  = "AllowExecutionFromEventBridge"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.zoho_modify_sprint_item.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.zoho_check_sprint_status_rule.arn
}
resource "aws_lambda_event_source_mapping" "dynamodb_to_lambda" {
  event_source_arn  = aws_dynamodb_table.zoho_waf_integration.stream_arn
  function_name     = aws_lambda_function.zoho_create_sprint_item.arn
  starting_position = "LATEST"
}