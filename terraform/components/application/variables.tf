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

variable "api_gateway_execution_arn" {
    type = string
    description = "The ARN Execution of the API Gateway"
}

variable "lambda_function_name" {
    type = string
    description = "The name of the Lambda function"
}

variable "dynamodb_table_name" {
    type = string
    description = "The name of the DynamoDB table"
}

variable "logging_level" {
    type = string
    description = "Logging level for the Lambda function"
}
