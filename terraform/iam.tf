# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

# Create an IAM role for the Lambda function
resource "aws_iam_role" "zoho_lambda_role" {
  name = "zoho_lambda_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "zoho_lambda_role_policy" {
  name = "zoho_lambda_role_policy"
  role = aws_iam_role.zoho_lambda_role.id

  policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            # {
            #     Effect   = "Allow",
            #     Action   = "ssm:GetParameter",
            #     Resource = local.ssm_parameter_arns
            # },
            {
                Effect   = "Allow",
                Action   = "secretsmanager:GetSecretValue",
                Resource = local.zoho_auth_secret_arn
            },
            {
                Effect   = "Allow",
                Action   = [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Scan"
                ],
                Resource = local.zoho_waf_integration_table_arn
            },
            {
                Effect   = "Allow",
                Action   = [
                    "dynamodb:GetRecords",
                    "dynamodb:GetShardIterator",
                    "dynamodb:DescribeStream",
                    "dynamodb:ListStreams"
                ],
                Resource = "${aws_dynamodb_table.zoho_waf_integration.stream_arn}"
            },
            {
                Action = [
                  "dynamodb:GetRecords",
                  "dynamodb:GetShardIterator",
                  "dynamodb:DescribeStream",
                  "dynamodb:ListStreams"
                ]
                Resource = "${aws_dynamodb_table.zoho_waf_integration.stream_arn}"
                Effect = "Allow"
            },
            {
                Effect   = "Allow",
                Action   = "lambda:InvokeFunction",
                Resource = local.waf_update_item_lambda_arn
            }

        ]
    })
}

# Create an IAM role for the Lambda function WAF Create item
resource "aws_iam_role" "waf_lambda_role" {
  name = "waf_lambda_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "waf_lambda_role_policy" {
  name = "waf_lambda_role_policy"
  role = aws_iam_role.waf_lambda_role.id

  policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Effect   = "Allow",
                Action   = [
                    "wellarchitected:ListLensReviewImprovements",
                    "wellarchitected:ListAnswers",
                    "wellarchitected:UpdateAnswer"
                ],
                Resource = "*"
            },
            {
                Effect   = "Allow",
                Action   = [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Scan"
                ],
                Resource = local.zoho_waf_integration_table_arn
            },
            {
                Effect   = "Allow",
                Action   = "lambda:InvokeFunction",
                Resource = local.zoho_create_sprint_item_lambda_arn
            }
        ]
    })
}
