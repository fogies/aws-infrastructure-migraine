/*
 * Tag created resources.
 */
locals {
  tags = {
    "scope-aws-infrastructure/terraform_instance": ""
  }
}

/*
 * ID of the Minikube AMI.
 */
module "minikube_ami" {
  source = "github.com/fogies/aws-infrastructure//terraform_common/minikube_ami"

  # Migraine
  owner_id = "409694990553"
  instance_type = "t3.medium"
  docker_volume_size = "50"
  build_timestamp = "20211108020557"
}

/*
 * Instance of Minikube Helm.
 */
module "minikube_instance" {
  source = "github.com/fogies/aws-infrastructure//terraform_common/minikube_instance"

  name = "instance"

  ami_id = module.minikube_ami.id
  aws_instance_type = "t3.medium"

  create_vpc = true
  availability_zone = "us-east-1a"

  eip_id = var.eip_id
  eip_public_ip = var.eip_public_ip

  tags = local.tags
}
