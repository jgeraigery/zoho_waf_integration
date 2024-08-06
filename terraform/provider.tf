# © Copyright Kyndryl, Inc. 2024
# Copyright contributors to the Zoho WAF Integration project.
# This file is part of an application that is distributed under the MIT License.
# Maintainers: Sujith R Pillai <s.r.pillai@kyndryl.com>, Jigar Kapasi <jigar.kapasi@kyndryl.com>

# Terraform provider for aws
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      ProjectName = var.project_name_tag
      ResourceName = var.resource_name_tag
    }
  }
}