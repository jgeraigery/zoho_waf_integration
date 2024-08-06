# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

# Create a Dynamo DB table to store the AWS WAF and Zoho Sprint API correlation
resource "aws_dynamodb_table" "zoho_waf_integration" {
    name           = "zoho_waf_integration"
    billing_mode   = "PAY_PER_REQUEST"
    hash_key       = "QuestionId"
    range_key      = "ImprovementItem" 
    attribute {
        name = "QuestionId"
        type = "S"
    }
    attribute {
        name = "ImprovementItem"
        type = "S"
    }
    stream_enabled = true
    stream_view_type = "NEW_AND_OLD_IMAGES"
}