# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

# Create an SSM Parameter for storing the Zoho Sprint ID
resource "aws_ssm_parameter" "zoho_token_url" {
  name  = "/zoho/zoho_token_url"
  type  = "String"
  value = var.zoho_token_url
}
resource "aws_ssm_parameter" "zoho_base_url" {
  name  = "/zoho/zoho_base_url"
  type  = "String"
  value = var.zoho_base_url
}
resource "aws_ssm_parameter" "zoho_team_id" {
  name  = "/zoho/zoho_team_id"
  type  = "String"
  value = var.zoho_team_id
}
resource "aws_ssm_parameter" "zoho_project_id" {
  name  = "/zoho/zoho_project_id"
  type  = "String"
  value = var.zoho_project_id
}
resource "aws_ssm_parameter" "zoho_sprint_id" {
  name  = "/zoho/zoho_sprint_id"
  type  = "String"
  value = var.zoho_sprint_id
}
resource "aws_ssm_parameter" "zoho_sprint_item_type_id" {
  name  = "/zoho/zoho_sprint_item_type_id"
  type  = "String"
  value = var.zoho_sprint_item_type_id
}
resource "aws_ssm_parameter" "zoho_risks_to_priority_mapping" {
  name  = "/zoho/zoho_risks_to_priority_mapping"
  type  = "String"
  value = jsonencode(var.zoho_risks_to_priority_mapping)
}
resource "aws_ssm_parameter" "zoho_status_id_mapping" {
  name  = "/zoho/zoho_status_id_mapping"
  type  = "String"
  value = jsonencode(var.zoho_status_id_mapping)
}