# =============================================================================
# MODULES/EC2/MAIN.TF - Module EC2 Fode-DevOps (Sécurisé)
# =============================================================================

# AMI Amazon Linux 2023 (gratuite)
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group pour l'instance web Fode-DevOps (Sécurisé)
resource "aws_security_group" "web" {
  name_prefix = "${var.project_name}-${var.environment}-web-"
  description = "Security group for web server - Fode-DevOps"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from Load Balancer only"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    # Remplacer par les CIDR des Load Balancers ou utiliser security group reference
    cidr_blocks = [var.vpc_cidr] # Restricition au VPC seulement
  }

  ingress {
    description = "HTTPS from Load Balancer only"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    # Remplacer par les CIDR des Load Balancers ou utiliser security group reference
    cidr_blocks = [var.vpc_cidr] # Restriction au VPC seulement
  }

  ingress {
    description = "SSH from specific IP only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["54.76.235.211/32"] # Votre IP spécifique
  }

  # Egress restrictif - seulement HTTPS pour les mises à jour
  egress {
    description = "HTTPS outbound for updates"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "HTTP outbound for package repos"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "DNS outbound"
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-web-sg"
  }
}

# Rôle IAM pour l'instance EC2
resource "aws_iam_role" "ec2_role" {
  name_prefix = "${var.project_name}-${var.environment}-ec2-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2-role"
  }
}

# Policy pour les logs CloudWatch
resource "aws_iam_role_policy" "ec2_cloudwatch_policy" {
  name_prefix = "${var.project_name}-${var.environment}-cloudwatch-"
  role        = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Instance Profile pour le rôle IAM
resource "aws_iam_instance_profile" "ec2_profile" {
  name_prefix = "${var.project_name}-${var.environment}-ec2-"
  role        = aws_iam_role.ec2_role.name

  tags = {
    Name = "${var.project_name}-${var.environment}-ec2-profile"
  }
}

# Paire de clés Fode-DevOps
resource "aws_key_pair" "main" {
  key_name   = var.key_name
  public_key = file("${path.module}/../../keys/id_rsa.pub")

  tags = {
    Name = "${var.project_name}-${var.environment}-key"
  }
}

# Instance EC2 Fode-DevOps (Free Tier + Sécurisée)
resource "aws_instance" "web" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.main.key_name
  subnet_id                   = var.private_subnet_id # Utiliser un subnet privé
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = false # Pas d'IP publique directe
  user_data                   = file("${path.module}/user_data.sh")
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
  
  # Surveillance détaillée activée
  monitoring = true
  
  # EBS optimisé (si supporté par le type d'instance)
  ebs_optimized = true

  # Configuration des métadonnées sécurisée (IMDSv2 obligatoire)
  metadata_options {
    http_endpoint               = "enabled"
    http_put_response_hop_limit = 1
    http_tokens                 = "required" # IMDSv2 obligatoire
    instance_metadata_tags      = "enabled"
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = 30 # Free Tier: jusqu'à 30 GB
    encrypted   = true
    # Utiliser une clé KMS personnalisée pour plus de sécurité
    # kms_key_id = aws_kms_key.ebs.arn
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-web-server"
  }

  # Empêcher la suppression accidentelle
  lifecycle {
    prevent_destroy = false # Mettre à true en production
  }
}

# Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-${var.environment}-alb-"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-alb-sg"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnets

  enable_deletion_protection = false # Mettre à true en production

  tags = {
    Name = "${var.project_name}-${var.environment}-alb"
  }
}

# Target Group pour l'ALB
resource "aws_lb_target_group" "main" {
  name     = "${var.project_name}-${var.environment}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-tg"
  }
}

# Attachement de l'instance au Target Group
resource "aws_lb_target_group_attachment" "main" {
  target_group_arn = aws_lb_target_group.main.arn
  target_id        = aws_instance.web.id
  port             = 80
}

# Listener pour l'ALB
resource "aws_lb_listener" "main" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

# NAT Gateway pour accès sortant depuis le subnet privé
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-eip"
  }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = var.public_subnets[0] # Premier subnet public

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-gw"
  }

  depends_on = [aws_eip.nat]
}