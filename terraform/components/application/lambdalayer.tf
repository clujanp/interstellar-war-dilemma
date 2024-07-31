resource "aws_lambda_layer_version" "dependencies" {
  layer_name = "dependencies-layer"
  compatible_runtimes = ["python3.11"]

  filename = "dependencies.zip"
  source_code_hash = filebase64sha256("dependencies.zip")
  description = "Common dependencies layer for Lambda functions"
}