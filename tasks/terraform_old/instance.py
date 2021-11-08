from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.instance_helmfile
import aws_infrastructure.tasks.library.minikube
import aws_infrastructure.tasks.library.terraform
from invoke import Collection
from pathlib import Path

import tasks.terraform.eip

CONFIG_KEY = 'instance'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './terraform_old/terraform_instance'
HELM_REPO_DIR = './helm_repo'
STAGING_LOCAL_HELMFILE_DIR = './.staging/helmfile'
STAGING_REMOTE_HELM_DIR = './.staging/helm'
STAGING_REMOTE_HELMFILE_DIR = './.staging/helmfile'
INSTANCE_NAME = 'instance'
TERRAFORM_VARIABLES_PATH = Path(TERRAFORM_DIR, 'variables.generated.tfvars')

ns = Collection('instance')


# Define variables to provide to Terraform
def terraform_variables_factory(*, context):
    with tasks.terraform.eip.eip_read_only(context=context) as eip_read_only:
        eip_id = eip_read_only.output.id
        eip_public_ip = eip_read_only.output.public_ip

    return {
        'eip_id': eip_id,
        'eip_public_ip': eip_public_ip,
    }


ns_minikube = aws_infrastructure.tasks.library.minikube.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
    helm_repo_dir=HELM_REPO_DIR,
    staging_local_helmfile_dir=STAGING_LOCAL_HELMFILE_DIR,
    staging_remote_helm_dir=STAGING_REMOTE_HELM_DIR,
    staging_remote_helmfile_dir=STAGING_REMOTE_HELMFILE_DIR,
    instance_names=[INSTANCE_NAME],
    terraform_variables_factory=terraform_variables_factory,
    terraform_variables_path=TERRAFORM_VARIABLES_PATH,
)

compose_collection(
    ns,
    ns_minikube,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_without_state(
        terraform_dir=TERRAFORM_DIR,
        exclude=[
            'init',
            'helm-install',
            'helmfile-apply',
            'ssh-port-forward',
        ],
        exclude_without_state=[
            'destroy',
        ],
    )
)
