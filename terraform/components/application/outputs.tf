output "lambda_function_arn" {
  value = aws_lambda_function.app.arn
}

output "lambda_function_invoke_arn" {
  value = aws_lambda_function.app.invoke_arn
}

output "app_lambda_layer_arn" {
  value = aws_lambda_layer_version.dependencies.arn
}