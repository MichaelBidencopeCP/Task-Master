provider "aws" {
    region = "us-east-1"  
}
##############
# Networking #
##############

resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support = true
    tags = {
        Name = "${var.project}-vpc"
    }
}

resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.main.id
    tags = {
        Name = "${var.project}-igw"
    }
}

data "aws_availability_zones" "available" {}

resource "aws_subnet" "public" {
    count = 2
    vpc_id = aws_vpc.main.id
    cidr_block = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
    availability_zone = data.aws_availability_zones.available.names[count.index]
    map_public_ip_on_launch = true
    tags = {
        Name = "${var.project}-public-${count.index + 1}"
    }
}

resource "aws_route_table" "public" {
    vpc_id = aws_vpc.main.id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.igw.id
    }
    tags = {
        Name = "${var.project}-public-rt"
    }
}

resource "aws_route_table_association" "public_assoc" {
    count = 2
    subnet_id = aws_subnet.public[count.index].id
    route_table_id = aws_route_table.public.id
  
}

###################
# Security Groups #
###################

resource "aws_security_group" "alb" {
    name        = "${var.project}-alb-sg"
    description = "Allow HTTP and HTTPS traffic to ALB"
    vpc_id      = aws_vpc.main.id

    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = [var.ingress_cidr]
        description = "Allow HTTP from anywhere"
    }
    ingress {
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = [var.ingress_cidr]
        description = "Allow HTTPS from anywhere"
    }
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow all outbound traffic"
    }
    tags = {
        Name = "${var.project}-alb-sg"
    }
}

resource "aws_security_group" "ecs" {
    name        = "${var.project}-ecs-sg"
    description = "Allow traffic to ECS tasks"
    vpc_id      = aws_vpc.main.id

    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        security_groups = [aws_security_group.alb.id]
        description = "Allow HTTP from ALB"
    }
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow all outbound traffic"
    }
    tags = {
        Name = "${var.project}-ecs-sg"
    }
}

##################
# ECR repository #
##################

resource "aws_ecr_repository" "app" {
    name = "${var.project}-ecr-repo"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
        scan_on_push = true
    }
    tags = {
        Name = "${var.project}-ecr-repo"
    }
}

#################
# Load Balancer #
#################

resource "aws_lb" "alb" {
    name               = "${var.project}-alb"
    internal           = false
    load_balancer_type = "application"
    security_groups    = [aws_security_group.alb.id]
    subnets            = aws_subnet.public[*].id
    tags = {
        Name = "${var.project}-alb"
    }
}

resource "aws_lb_target_group" "tg" {
    name        = "${var.project}-tg"
    port        = 8000
    protocol    = "HTTP"
    vpc_id      = aws_vpc.main.id
    target_type = "ip"
    health_check {
        path                = var.health_check_path
        interval            = 30
        timeout             = 5
        healthy_threshold   = 2
        unhealthy_threshold = 2
        matcher             = "200-399"
    }
    tags = {
        Name = "${var.project}-tg"
    }
}

resource "aws_lb_listener" "http" {
    load_balancer_arn = aws_lb.alb.arn
    port              = 80
    protocol          = "HTTP"
    default_action {
        type             = "forward"
        target_group_arn = aws_lb_target_group.tg.arn
    }
}

#######
# IAM #
#######

data "aws_iam_policy_document" "ecs_task_assume_role" {
    statement {
        effect  = "Allow"
        actions = ["sts:AssumeRole"]
        principals {
            type        = "Service"
            identifiers = ["ecs-tasks.amazonaws.com"]
        }
    }
}

resource "aws_iam_role" "ecs_task_execution_role" {
    name               = "${var.project}-ecs-task-execution-role"
    assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
    role       = aws_iam_role.ecs_task_execution_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

#resource "aws_iam_role" "task_role" {
#  name               = "${var.project}-task-role"
#  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
#}

###################
# CloudWatch Logs #
###################

resource "aws_cloudwatch_log_group" "ecs" {
    name              = "/ecs/${var.project}"
    retention_in_days = 7
    tags = {
        Name = "${var.project}-log-group"
    }
}

###############
# ECS Cluster #
###############

resource "aws_ecs_cluster" "this" {
    name = "${var.project}-ecs-cluster"
}

resource "aws_ecs_task_definition" "task_definition" {
    family                   = "${var.project}-task"
    network_mode             = "awsvpc"
    requires_compatibilities = ["FARGATE"]
    cpu                      = "256"
    memory                   = "512"
    execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
    #task_role_arn            = aws_iam_role.task_role.arn

    container_definitions = jsonencode([
        {
            name      = "app"
            image     = "nginx:latest"
            essential = true
            portMappings = [
                {
                    containerPort = 80
                    hostPort      = 80
                    protocol      = "tcp"
                }
            ]
            logConfiguration = {
                logDriver = "awslogs"
                options = {
                    awslogs-group         = aws_cloudwatch_log_group.ecs.name
                    awslogs-region        = "us-east-1"
                    awslogs-stream-prefix = "app"
                }
            }
        }
    ])
}

resource "aws_ecs_service" "service_definition" {
    name            = "${var.project}-service"
    cluster         = aws_ecs_cluster.this.id
    task_definition = aws_ecs_task_definition.task_definition.arn
    desired_count   = 2
    launch_type     = "FARGATE"
    network_configuration {
        subnets         = aws_subnet.public[*].id
        security_groups = [aws_security_group.ecs.id]
        assign_public_ip = true
    }
    load_balancer {
        target_group_arn = aws_lb_target_group.tg.arn
        container_name   = "app"
        container_port   = 80
    }
    depends_on = [aws_lb_listener.http]
    tags = {
        Name = "${var.project}-service"
    }
  
}

######################################
# github action to push image to ECR #
######################################


resource "aws_iam_openid_connect_provider" "github" {
    url = "https://token.actions.githubusercontent.com"
    client_id_list = ["sts.amazonaws.com"]
    thumbprint_list = ["7560d6f40fa55195f740ee2b1b7c0b4836cbe103"]
}

resource "aws_iam_role" "github_actions" {
    name = "${var.project}-github-actions-role"
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Principal = {
                    Federated = aws_iam_openid_connect_provider.github.arn
                }
                Action = "sts:AssumeRoleWithWebIdentity"
                Condition = {
                    StringLike = {
                        "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
                        "token.actions.githubusercontent.com:sub" = "repo:MichaelBidencopeCP/Task-Master:*"
                    }
                }
            }
        ]
    })
}

resource "aws_iam_role_policy" "github_actions_ecr" {
    name = "${var.project}-github-actions-ecr-policy"
    role = aws_iam_role.github_actions.id

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage"
                ]
                Resource = "*"
            }
        ]
    })
}

resource "aws_iam_role_policy" "github_actions_ecs" {
    name = "${var.project}-github-actions-ecs-policy"
    role = aws_iam_role.github_actions.id

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "ecs:DescribeTaskDefinition",
                    "ecs:RegisterTaskDefinition",
                    "ecs:UpdateService",
                    "ecs:DescribeServices"
                ]
                Resource = "*"
            },
            {
                Effect = "Allow"
                Action = [
                    "iam:PassRole"
                ]
                Resource = aws_iam_role.ecs_task_execution_role.arn
            }
        ]
    })
}

resource "aws_iam_role_policy" "github_actions_secrets" {
    name        = "${var.project}-github-actions-secrets-policy"
    role        = aws_iam_role.github_actions.id
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret"
                ]
                Resource = var.secret_manager_jwt_arn
            }
        ]
    })
}