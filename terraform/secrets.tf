# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

# Create an AWS secrets manager secret for storing the Zoho Sprint API token
resource "aws_secretsmanager_secret" "zoho_authentication" {
    name                   = "zoho_authentication_for_waf"
    recovery_window_in_days = 7

    tags = {
        Name = "ZohoAuthentication"
    }
}

resource "aws_secretsmanager_secret_version" "zoho_auth_secrets" {
    secret_id     = aws_secretsmanager_secret.zoho_authentication.id

    secret_string = jsonencode({
        zoho_client_id     = var.zoho_client_id
        zoho_client_secret = var.zoho_client_secret
        zoho_refresh_token = var.zoho_refresh_token
    })
}
