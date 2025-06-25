# =============================================================================
# MODULES/EC2/MAIN.TF - Module EC2 Fode-DevOps
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

# Security Group pour l'instance web Fode-DevOps
resource "aws_security_group" "web" {
  name_prefix = "${var.project_name}-${var.environment}-web-"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # À restreindre à votre IP en production
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-web-sg"
  }
}

# Paire de clés Fode-DevOps
resource "aws_key_pair" "main" {
  key_name   = var.key_name
  public_key = file("C:/Users/Fode/.ssh/id_rsa.pub")

  tags = {
    Name = "${var.project_name}-${var.environment}-key"
  }
}

# Instance EC2 Fode-DevOps (Free Tier)
resource "aws_instance" "web" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.main.key_name
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true
  user_data                   = file("${path.module}/user_data.sh")

  root_block_device {
    volume_type = "gp3"
    volume_size = 30 # Free Tier: jusqu'à 30 GB
    encrypted   = true
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-web-server"
  }
}

# Elastic IP Fode-DevOps (gratuit si attaché)
resource "aws_eip" "web" {
  instance = aws_instance.web.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-eip"
  }

  depends_on = [aws_instance.web]
}
