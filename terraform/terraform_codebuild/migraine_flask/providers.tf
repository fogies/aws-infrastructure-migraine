/*
 * AWS Configuration.
 */
provider "aws" {
  profile = "aws-infrastructure-migraine"
  shared_credentials_file = "../../../secrets/aws/aws-infrastructure-migraine.credentials"

  # Must specify region, it will not be taken from the AWS configuration.
  # https://github.com/hashicorp/terraform-provider-aws/issues/687
  region  = "us-east-1"
}
