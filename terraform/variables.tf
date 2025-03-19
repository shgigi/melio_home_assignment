variable "database_name" {
  type = string
  nullable = false
  description = "Name of RDS Database to create"
}

variable "database_engine" {
  type = string
  nullable = false
  description = "Database engine, either MySQL or PostgreSQL"
  validation {
    condition = lower(var.database_engine)  == "mysql" || lower(var.database_engine) == "postgresql"
    error_message = "DatabaseEngine must be one of: [mysql, postgresql]"
  }
}

variable "environment" {
  type = string
  nullable = false
  description = "enviroment to deploy the database, either Dev or Prod"
  validation {
    condition = lower(var.environment) == "dev" || lower(var.environment) == "prod"
    error_message = "Environment must be one of: [dev, prod]"
  }
}