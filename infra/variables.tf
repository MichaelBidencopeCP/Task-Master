

variable "project" {
    description = "Project name for tagging and naming"
    type        = string
    default     = "task-master"
}

variable "ingress_cidr" {
  description = "Who can reach your ALB"
  type        = string
  default     = "0.0.0.0/0"
}

variable "health_check_path" {
    description = "Health check path for the ALB"
    type        = string
    #default     = "/api/health"
    default     = "/"
}

variable "secret_manager_jwt_arn" {
    description = "ARN of the AWS Secrets Manager secret"
    type        = string
    default     = ""
}