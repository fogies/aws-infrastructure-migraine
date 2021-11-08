/*
 * Tag created resources.
 */
locals {
  tags = {
    "scope-aws-infrastructure/terraform_instance": ""
  }
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_instance" {
  source = "github.com/fogies/aws-infrastructure//terraform_common/minikube_instance"

  name = "instance"

  ami_configuration = "amd64-medium"
  aws_instance_type = "t3.medium"

  create_vpc = true
  availability_zone = "us-east-1a"

  eip_id = var.eip_id
  eip_public_ip = var.eip_public_ip

  tags = local.tags
}
