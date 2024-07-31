output "lambda_function_arn" {
  value = aws_lambda_function.auth.arn
}

output "lambda_function_invoke_arn" {
  value = aws_lambda_function.auth.invoke_arn
}

output "user_pool_id" {
  value = aws_cognito_user_pool.user_pool.id
}

output "user_pool_client_id" {
  value = aws_cognito_user_pool_client.user_pool_client.id
}

output "user_pool_client_secret" {
  value = aws_cognito_user_pool_client.user_pool_client.client_secret
}

output "user_pool_domain" {
  value = aws_cognito_user_pool_domain.user_pool_domain.domain
}