terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"
}


module "application" {
  source = "./components/application"

  environment                   = var.environment
  stage                         = var.stage
  aws_account_id                = var.aws_account_id
  region                        = var.region
  app_name                      = var.app_app_name
  api_gateway_execution_arn     = aws_apigatewayv2_api.http_api.execution_arn
  lambda_function_name          = var.app_lambda_function_name
  dynamodb_table_name           = var.dynamodb_table_name
  logging_level                 = var.logging_level
}


module "authorized" {
  source = "./components/authorized"

  environment                   = var.environment
  stage                         = var.stage
  aws_account_id                = var.aws_account_id
  region                        = var.region
  app_name                      = var.auth_app_name
  api_gateway_execution_arn     = aws_apigatewayv2_api.http_api.execution_arn
  lambda_function_name          = var.auth_lambda_function_name
  app_lambda_layer_arn          = module.application.app_lambda_layer_arn
  dynamodb_table_name           = var.dynamodb_table_name
  logging_level                 = var.logging_level
  cognito_user_pool_name        = var.cognito_user_pool_name
  cognito_user_pool_client_name = var.cognito_user_pool_client_name
  cognito_user_pool_domain_name = var.cognito_user_pool_domain_name
}
