resource "aws_iam_role" "lambda_exec_role" {
  name = "${var.app_name}_lambda_exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })

    tags = {
      Name = "${var.app_name}_lambda_exec"
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.app_name}_lambda_policy"
  description = "Lambda policy for ${var.app_name}"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:*",
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}


resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name        = "${var.app_name}_lambda_dynamodb_policy"
  description = "IAM policy for DynamoDB access from Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:PutItem",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:dynamodb:${var.region}:${var.aws_account_id}:table/${var.dynamodb_table_name}"
      },
    ]
  })
}

resource "aws_iam_policy" "lambda_cognito_policy" {
  name        = "${var.app_name}_lambda_cognito_policy"
  description = "IAM policy for Cognito access from Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "cognito-idp:SignUp",
          "cognito-idp:ConfirmSignUp",
          "cognito-idp:InitiateAuth",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:cognito-idp:${var.region}:${var.aws_account_id}:userpool/${aws_cognito_user_pool.user_pool.id}"
      },
    ]
  })
}

resource "aws_iam_policy" "lambda_cognito_actions_policy" {
  name        = "${var.app_name}_lambda_cognito_actions_policy"
  description = "IAM policy for Cognito actions from Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "cognito-idp:SignUp",
          "cognito-idp:ConfirmSignUp",
          "cognito-idp:InitiateAuth",
        ]
        Effect   = "Allow"
        Resource = "arn:aws:cognito-idp:${var.region}:${var.aws_account_id}:userpool/${aws_cognito_user_pool.user_pool.id}"
      },
    ]
  })
}


resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_cognito_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_cognito_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_cognito_actions_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_cognito_actions_policy.arn
}
