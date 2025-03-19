output "db_password_info" {
  value = aws_db_instance.db_instance.master_user_secret
  description = "Information about the database's password secret."
}

output "db_username_info" {
  value = aws_ssm_parameter.db_username.name
  description = "SSM parameter where the database's username is stored."
}

output "db_arn" {
  value = aws_db_instance.db_instance.arn
  description = "Database instance ARN."
}

