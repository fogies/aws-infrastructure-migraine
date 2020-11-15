/*
 * ID of the Elastic IP.
 */
output "id" {
  value = aws_eip.ip.id
}

/*
 * Public IP of the Elastic IP.
 */
output "public_ip" {
  value = aws_eip.ip.public_ip
}
