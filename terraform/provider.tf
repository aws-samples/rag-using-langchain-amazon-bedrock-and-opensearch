terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Name = var.name
    }
  }
}

## This is for demo porpuses, for production use, use a remote state backed by Amazon S3
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
