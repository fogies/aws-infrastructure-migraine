/*
 * Tag created resources.
 */
locals {
  tags = {
    "aws-infrastructure-migraine/terraform_ecr": ""
  }
}

/*
 * Instance of ECR Simple.
 */
module "ecr" {
  source = "github.com/fogies/aws-infrastructure//terraform_common/ecr"

  names = [
    "aws_infrastructure_migraine/migraine_flask",
  ]
}
