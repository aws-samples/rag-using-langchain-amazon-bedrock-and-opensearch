resource "random_password" "pass" {
  length      = 16
  special     = false
  min_numeric = 1
  min_special = 1
  min_upper   = 1
}

resource "aws_secretsmanager_secret" "secret" {
  name_prefix = var.name
}

resource "aws_secretsmanager_secret_version" "secret" {
  secret_id     = aws_secretsmanager_secret.secret.id
  secret_string = random_password.pass.result
}

output "secret_name" {
  value = aws_secretsmanager_secret.secret.name
}