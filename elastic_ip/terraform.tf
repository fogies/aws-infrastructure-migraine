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
 * An elastic IP that will persist if we create/destroy our instance.
 */
resource "aws_eip" "ip" {
}
