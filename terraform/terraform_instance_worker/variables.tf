/*
 * ID of the Elastic IP.
 */
variable "eip_id" {
  type = string
}

/*
 * Public IP of the Elastic IP.
 */
variable "eip_public_ip" {
  type = string
}

/*
 * VPC in which to create the instance.
 */
variable "vpc_id" {
  type = string
  default = null
}

/*
 * Default security group ID for the VPC.
 */
variable "vpc_default_security_group_id" {
  type = string
  default = null
}

/*
 * Subnet in which to create the instance.
 */
variable "subnet_id" {
  type = string
  default = null
}
