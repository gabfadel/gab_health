terraform {
  required_version = "1.11.4"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.7.0"
    }
  }
  backend "s3" {
    bucket       = "gab-health-tfstate"
    key          = "terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}


provider "aws" {
  region = var.aws_region
}
