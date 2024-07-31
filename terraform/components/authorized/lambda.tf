resource "aws_lambda_function" "auth" {
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "auth_wsgi_handler.handler"
  runtime          = "python3.11"
  filename         = "lambda_function.zip"
  source_code_hash = filebase64sha256("lambda_function.zip")
  layers           = [var.app_lambda_layer_arn]

  environment {
    variables = {
      ENVIRONMENT               = var.environment
      STAGE                     = var.stage
      LOGGING_LEVEL             = var.logging_level
      AWS_DYNAMODB_TABLE_NAME   = var.dynamodb_table_name
      COGNITO_APP_CLIENT_ID     = aws_cognito_user_pool_client.user_pool_client.id
      # FUTURE: Manage this secret in AWS Secrets Manager
      COGNITO_APP_CLIENT_SECRET = aws_cognito_user_pool_client.user_pool_client.client_secret
    }
  }
}

resource "aws_lambda_permission" "api_gw_auth" {
  statement_id  = "AllowExecutionFromAPIGatewayAuth"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth.arn
  principal     = "apigateway.amazonaws.com"

  source_arn    = "${var.api_gateway_execution_arn}/*/*"
}