/*
 * Explicit configuration of providers.
 */
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.9.0"
    }
  }
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_helm_instance" {
  source = "github.com/fogies/aws-infrastructure//terraform_common/minikube_helm"

  instance_name = "instance"
  instance_dir = "instance"
  tasks_config_context = "minikube_helm_instance"

  aws_availability_zone = "us-east-1a"
  ami_architecture = "amd64"
  aws_instance_type = "t3.medium"

  eip = true
  eip_id = var.eip_id
  eip_public_ip = var.eip_public_ip

  tags = {
  }
}
