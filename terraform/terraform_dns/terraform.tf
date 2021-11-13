/*
 * Zone with DNS records.
 */
module "hosted_zone" {
  source = "github.com/fogies/aws-infrastructure//terraform_common/hosted_zone"

  aws_provider = {
    profile = "aws-infrastructure-migraine"
    shared_credentials_file = "../../secrets/aws/aws-infrastructure-migraine.credentials"

    # Must specify region, it will not be taken from the AWS configuration.
    # https://github.com/hashicorp/terraform-provider-aws/issues/687
    region  = "us-east-1"
  }

  name = "migraineapp.org"

  address_records = [
    /* Root Domain */
    {
      name = "migraineapp.org",
      ip = var.eip_public_ip,
    },
  ]
}
