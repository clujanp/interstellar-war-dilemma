output "app_lambda_function_arn" {
  value = module.application.lambda_function_arn
}

output "auth_lambda_function_arn" {
  value = module.authorized.lambda_function_arn
}

output "api_gateway_url" {
  value = aws_apigatewayv2_stage.default.invoke_url
}

output "user_pool_id" {
  value = module.authorized.user_pool_id
}

output "user_pool_client_id" {
  value = module.authorized.user_pool_client_id
}

output "user_pool_client_secret" {
  value = module.authorized.user_pool_client_secret
  sensitive = true
}

output "user_pool_domain" {
  value = module.authorized.user_pool_domain
}
