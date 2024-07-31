resource "aws_dynamodb_table" "main" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "entity"
  range_key    = "version"

  attribute {
    # like Role, Policy, User, etc.
    name = "entity"
    type = "S"
  }

  attribute {
    # like v0_uuid, v1_uuid, etc.
    name = "version"
    type = "S"
  }

  tags = {
    Name = var.dynamodb_table_name
  }
}