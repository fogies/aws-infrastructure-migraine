/*
 * AWS Configuration.
 */
provider "aws" {
  profile = "aws-infrastructure-migraine"
  shared_credentials_file = "../../secrets/aws/aws-infrastructure-migraine.credentials"

  region  = "us-east-1"
}
