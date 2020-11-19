from collections import namedtuple
import aws_infrastructure.task_templates

CONFIG_KEY = 'terraform_elastic_ip'

init = aws_infrastructure.task_templates.terraform.template_init(
    config_key=CONFIG_KEY
)
apply = aws_infrastructure.task_templates.terraform.template_apply(
    config_key=CONFIG_KEY,
    init=init
)
destroy = aws_infrastructure.task_templates.terraform.template_destroy(
    config_key=CONFIG_KEY,
    init=init
)
output = aws_infrastructure.task_templates.terraform.template_output(
    config_key=CONFIG_KEY,
    init=init,
    output_tuple_factory=namedtuple('elastic_ip', ['id', 'public_ip'])
)

elastic_ip = aws_infrastructure.task_templates.terraform.template_context_manager(
    init=init,
    # apply=apply,
    output=output,
    # destroy=destroy
)
