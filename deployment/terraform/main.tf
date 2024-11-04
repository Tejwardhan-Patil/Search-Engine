# Provider configuration (AWS)
provider "aws" {
  region = "us-west-2"
}

# Define the VPC
resource "aws_vpc" "search_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "search-engine-vpc"
  }
}

# Internet Gateway for public access
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.search_vpc.id
  tags = {
    Name = "search-engine-igw"
  }
}

# Create a subnet for the VPC
resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.search_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
  map_public_ip_on_launch = true
  tags = {
    Name = "search-engine-subnet"
  }
}

# Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.search_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "search-engine-rt"
  }
}

# Associate route table with subnet
resource "aws_route_table_association" "public_rt_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# Security Group for EC2 Instances
resource "aws_security_group" "web_sg" {
  vpc_id = aws_vpc.search_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "search-engine-sg"
  }
}

# EC2 instance for the web crawler
resource "aws_instance" "crawler_instance" {
  ami           = "ami-0c55b159cbfafe1f0" # Amazon Linux 2 AMI
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public_subnet.id
  security_groups = [aws_security_group.web_sg.name]

  tags = {
    Name = "search-engine-crawler"
  }
}

# EC2 instance for the indexing service
resource "aws_instance" "indexing_instance" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public_subnet.id
  security_groups = [aws_security_group.web_sg.name]

  tags = {
    Name = "search-engine-indexing"
  }
}

# S3 bucket for storage
resource "aws_s3_bucket" "storage_bucket" {
  bucket = "search-engine-storage"

  tags = {
    Name = "search-engine-storage"
  }
}

# RDS Instance for metadata storage
resource "aws_db_instance" "metadata_db" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "mysql"
  instance_class       = "db.t2.micro"
  db_name              = "metadata"
  username             = "admin"
  password             = "password123"
  publicly_accessible  = true
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
}

# RDS Subnet group for the database
resource "aws_db_subnet_group" "main" {
  name = "search-engine-db-subnet-group"
  subnet_ids = [aws_subnet.public_subnet.id]

  tags = {
    Name = "search-engine-db-subnet-group"
  }
}

# Output the public IPs of EC2 instances
output "crawler_instance_public_ip" {
  value = aws_instance.crawler_instance.public_ip
}

output "indexing_instance_public_ip" {
  value = aws_instance.indexing_instance.public_ip
}