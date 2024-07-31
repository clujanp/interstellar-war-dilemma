resource "aws_iam_role" "apigateway_logging_role" {
  name = "${var.app_name}_apigateway_logging_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "apigateway.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_policy" "apigateway_logging_policy" {
  name        = "${var.app_name}_apigateway_logging_policy"
  description = "IAM policy for API Gateway to write logs to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "apigateway_lambda_policy" {
  name        = "${var.app_name}_apigateway_lambda_policy"
  description = "IAM policy for API Gateway to invoke Lambda functions"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:InvokeFunction"
        ],
        Resource = "*"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "apigateway_logging" {
  role       = aws_iam_role.apigateway_logging_role.name
  policy_arn = aws_iam_policy.apigateway_logging_policy.arn
}

resource "aws_iam_role_policy_attachment" "apigateway_lambda" {
  role       = aws_iam_role.apigateway_logging_role.name
  policy_arn = aws_iam_policy.apigateway_lambda_policy.arn
}