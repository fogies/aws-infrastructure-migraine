from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.codebuild
import aws_infrastructure.tasks.library.terraform
from datetime import datetime
from invoke import Collection

import tasks.terraform.ecr

CONFIG_KEY = 'server_flask'
TERRAFORM_BIN = './bin/terraform.exe'
TERRAFORM_DIR = './terraform/terraform_codebuild/server_flask'
STAGING_LOCAL_DIR = './.staging/codebuild/server_flask'
AWS_PROFILE = 'aws-infrastructure-migraine'
AWS_SHARED_CREDENTIALS_PATH = './secrets/aws/aws-infrastructure-migraine.credentials'
AWS_CONFIG_PATH = './secrets/aws/aws-infrastructure-migraine.config'
SOURCE_DIR = './docker/server_flask'
CODEBUILD_PROJECT_NAME = 'aws_infrastructure_migraine_server_flask'

BUILD_TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M')


def codebuild_environment_variables_factory(*, context):
    with tasks.terraform.ecr.ecr_read_only(context=context) as ecr:
        return {
            'REGISTRY_URL': ecr.output.registry_url,
            'REPOSITORY': 'aws_infrastructure_migraine/server_flask',
            'REPOSITORY_URL': ecr.output.repository_urls['aws_infrastructure_migraine/server_flask'],
            'REPOSITORY_TAGS': 'latest {}'.format(BUILD_TIMESTAMP)
        }


ns = Collection('codebuild')

ns_codebuild = aws_infrastructure.tasks.library.codebuild.create_tasks(
    config_key=CONFIG_KEY,
    terraform_bin=TERRAFORM_BIN,
    terraform_dir=TERRAFORM_DIR,
    staging_local_dir=STAGING_LOCAL_DIR,
    aws_profile=AWS_PROFILE,
    aws_shared_credentials_path=AWS_SHARED_CREDENTIALS_PATH,
    aws_config_path=AWS_CONFIG_PATH,
    source_dir=SOURCE_DIR,
    codebuild_project_name=CODEBUILD_PROJECT_NAME,
    codebuild_environment_variables_factory=codebuild_environment_variables_factory,
)

compose_collection(
    ns,
    ns_codebuild,
    sub=False,
    exclude=aws_infrastructure.tasks.library.terraform.exclude_without_state(
        terraform_dir=TERRAFORM_DIR,
        exclude=[
            'init',
            'apply',
        ],
        exclude_without_state=[
            'destroy'
        ],
    )
)
