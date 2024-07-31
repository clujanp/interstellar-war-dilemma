resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.app_name}-api"
  protocol_type = "HTTP"
}


resource "aws_apigatewayv2_integration" "app_lambda" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = module.application.lambda_function_invoke_arn
  payload_format_version = "2.0"
  credentials_arn = aws_iam_role.apigateway_logging_role.arn
}

resource "aws_apigatewayv2_integration" "auth_lambda" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = module.authorized.lambda_function_invoke_arn
  payload_format_version = "2.0"
  credentials_arn = aws_iam_role.apigateway_logging_role.arn
}


variable "http_methods" {
  default = ["GET", "POST", "PUT", "DELETE"]
}


resource "aws_apigatewayv2_authorizer" "jwt_authorizer" {
  name                   = "JWTAuthorizer"
  api_id                 = aws_apigatewayv2_api.http_api.id
  authorizer_type        = "JWT"
  identity_sources       = ["$request.header.Authorization"]
  jwt_configuration {
    audience             = [module.authorized.user_pool_client_id]
    issuer               = "https://cognito-idp.${var.region}.amazonaws.com/${module.authorized.user_pool_id}"
  }
}


resource "aws_apigatewayv2_route" "app_resources" {
  api_id              = aws_apigatewayv2_api.http_api.id
  route_key           = "GET /resources/{proxy+}"
  target              = "integrations/${aws_apigatewayv2_integration.app_lambda.id}"
  authorizer_id       = aws_apigatewayv2_authorizer.jwt_authorizer.id
  authorization_type  = "JWT"
}

resource "aws_apigatewayv2_route" "app_policies" {
  count               = length(var.http_methods)
  api_id              = aws_apigatewayv2_api.http_api.id
  route_key           = "${var.http_methods[count.index]} /policies/{proxy+}"
  target              = "integrations/${aws_apigatewayv2_integration.app_lambda.id}"
  authorizer_id       = aws_apigatewayv2_authorizer.jwt_authorizer.id
  authorization_type  = "JWT"
}

resource "aws_apigatewayv2_route" "app_roles" {
  count               = length(var.http_methods)
  api_id              = aws_apigatewayv2_api.http_api.id
  route_key           = "${var.http_methods[count.index]} /roles/{proxy+}"
  target              = "integrations/${aws_apigatewayv2_integration.app_lambda.id}"
  authorizer_id       = aws_apigatewayv2_authorizer.jwt_authorizer.id
  authorization_type  = "JWT"
}

resource "aws_apigatewayv2_route" "app_users" {
  count               = length(var.http_methods)
  api_id              = aws_apigatewayv2_api.http_api.id
  route_key           = "${var.http_methods[count.index]} /users/{proxy+}"
  target              = "integrations/${aws_apigatewayv2_integration.app_lambda.id}"
  authorizer_id       = aws_apigatewayv2_authorizer.jwt_authorizer.id
  authorization_type  = "JWT"
}

resource "aws_apigatewayv2_route" "app_groups" {
  count               = length(var.http_methods)
  api_id              = aws_apigatewayv2_api.http_api.id
  route_key           = "${var.http_methods[count.index]} /groups/{proxy+}"
  target              = "integrations/${aws_apigatewayv2_integration.app_lambda.id}"
  authorizer_id       = aws_apigatewayv2_authorizer.jwt_authorizer.id
  authorization_type  = "JWT"
}

resource "aws_apigatewayv2_route" "auth" {
  api_id        = aws_apigatewayv2_api.http_api.id
  route_key     = "POST /auth/{proxy+}"
  target        = "integrations/${aws_apigatewayv2_integration.auth_lambda.id}"
}


resource "aws_cloudwatch_log_group" "apigateway_log_group" {
  name              = "/aws/apigateway/${var.app_name}-logs"
  retention_in_days = 14
}


resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigateway_log_group.arn
    format          = jsonencode({
      requestId: "$context.requestId",
      ip: "$context.identity.sourceIp",
      caller: "$context.identity.caller",
      protocol: "$context.protocol",
      user: "$context.identity.user",
      requestTime: "$context.requestTime",
      httpMethod: "$context.httpMethod",
      resourcePath: "$context.resourcePath",
      path: "$context.path"
      status: "$context.status",
      responseLength: "$context.responseLength"
      errorResponseType: "$context.error.responseType",
      errorMessage: "$context.error.message",
      integrationStatus: "$context.integrationStatus",
      integrationError: "$context.integration.error",
    })
  }
}