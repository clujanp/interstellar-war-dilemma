variable "environment" {
    type = string
    description = "specify the environment for the resources"
}

variable "stage" {
    type = string
    description = "deployment environment acronyms"
}

variable "region" {
    type = string
    description = "The AWS region where the resources will be deployed"
}

variable "aws_account_id" {
    type = string
    description = "The AWS account ID"
}

variable "app_name" {
    type = string
    description = "The name of the application"
}

variable "app_app_name" {
    type = string
    description = "The name of the app component"
}

variable "auth_app_name" {
    type = string
    description = "The name of the auth component"
}

variable "dynamodb_table_name" {
    type = string
    description = "The name of the DynamoDB table"
}

variable "app_lambda_function_name" {
    type = string
    description = "The name of app component Lambda function"
}

variable "auth_lambda_function_name" {
    type = string
    description = "The name of auth component Lambda function"
}

variable "logging_level" {
    type = string
    description = "Logging level for the Lambda function"
}

variable "cognito_user_pool_name" {
    type = string
    description = "Cogntio User Pool Name"
}

variable "cognito_user_pool_client_name" {
    type = string
    description = "Cogntio User Pool Client Name"
}

variable "cognito_user_pool_domain_name" {
    type = string
    description = "Cogntio User Pool Domain Name"
}
