terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.91.0"
    }
  }
}

provider "aws" {
  
}

resource "aws_db_instance" "db_instance" {
  db_name = var.database_name
  identifier = var.database_name
  engine = local.database_engine
  instance_class = local.environment == "prod" ? "db.4tg.micro" : "db.t3.micro"
  allocated_storage = 20
  storage_type = "gp2"
  storage_encrypted = true
  manage_master_user_password = true
  username = local.database_engine == "postgresql" ? "postgres" : "root"
  iam_database_authentication_enabled = true
  skip_final_snapshot = true
}


resource "aws_ssm_parameter" "db_username" {
  name = "/databases/${local.database_engine}/${var.database_name}/username"
  type = "String"
  value = aws_db_instance.db_instance.username
}

resource "aws_ssm_parameter" "db_password_secret" {
  name = "/databases/${local.database_engine}/${var.database_name}/secret"
  type = "String"
  insecure_value = aws_db_instance.db_instance.master_user_secret[0].secret_arn
}
