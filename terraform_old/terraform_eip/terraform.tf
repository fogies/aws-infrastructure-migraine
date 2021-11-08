/*
 * Tag created resources.
 */
locals {
  tags = {
    "aws-infrastructure-migraine/terraform_eip": ""
  }
}

/*
 * An elastic IP.
 */
resource "aws_eip" "eip" {
  tags = local.tags
}
