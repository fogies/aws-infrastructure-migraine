import aws_infrastructure.task_templates

import terraform_elastic_ip

CONFIG_KEY = 'terraform_instance'


def variables(*, context):
    elastic_ip_output = terraform_elastic_ip.elastic_ip(context=context).output

    return {
        'eip_id': elastic_ip_output.id,
        'eip_public_ip': elastic_ip_output.public_ip
    }


init = aws_infrastructure.task_templates.terraform.template_init(
    config_key=CONFIG_KEY
)
apply = aws_infrastructure.task_templates.terraform.template_apply(
    config_key=CONFIG_KEY,
    init=init,
    variables=variables
)
destroy = aws_infrastructure.task_templates.terraform.template_destroy(
    config_key=CONFIG_KEY,
    init=init,
    variables=variables
)
