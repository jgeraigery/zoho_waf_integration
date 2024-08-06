# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

# Terraform Variables
variable "aws_region" {
  description = "The AWS region to deploy to"
  default     = "us-east-1"
}

variable "project_name_tag" {
  description = "The name of the project"
}
variable "resource_name_tag" {
  description = "The name of the resource"
}

# DynamoDB Variables
variable "dynamodb_table" {
  description = "The name of the DynamoDB table for storing the WAF - Zoho Sprint mapping"
}

# Zoho authentication variables
variable "zoho_client_id" {
  description = "The Zoho Sprint Client ID"
}
variable "zoho_client_secret" {
  description = "The Zoho Sprint Client Secret"
}
variable "zoho_refresh_token" {
  description = "The Zoho Sprint Refresh Token"
}

# Zoho Sprint Variables
variable "zoho_token_url" {
  description = "The Zoho Sprint Token URL"
}
variable "zoho_base_url" {
  description = "The Zoho Sprint Base URL"
}
variable "zoho_team_id" {
  description = "The Zoho Sprint Team ID"
}
variable "zoho_project_id" {
  description = "The Zoho Sprint Project ID"
}
variable "zoho_sprint_id" {
  description = "The Zoho Sprint ID"
}
variable "zoho_sprint_item_type_id" {
  description = "The Zoho Sprint Item Type (Story, Task, or Issue) ID"
}

variable "zoho_risks_to_priority_mapping" {
  description = "The mapping of Zoho Sprint Risk to Priority"
  type        = map(string)
}

variable "zoho_status_id_mapping" {
  description = "The mapping of Zoho Sprint Status to ID"
  type        = map(string)
}