import aws_infrastructure.tasks.library.instance_helmfile
from invoke import Collection
import ruamel.yaml
from pathlib import Path

import tasks.terraform.ecr

CONFIG_KEY = 'helmfile'
STAGING_LOCAL_HELMFILE_DIR = './.staging/helmfile'
STAGING_REMOTE_HELM_DIR = './.staging/helm'
STAGING_REMOTE_HELMFILE_DIR = './.staging/helmfile'

INSTANCE_TERRAFORM_DIR = './terraform/terraform_instance'
INSTANCE_NAME = 'instance'
HELMFILE_PATH = './helmfile/helmfile.yaml'
HELMFILE_CONFIG_PATH = './helmfile/helmfile_config.yaml'
SSH_CONFIG_PATH = Path(INSTANCE_TERRAFORM_DIR, INSTANCE_NAME, 'ssh_config.yaml')

COUCHDB_CONFIG_PATH = './secrets/configuration/dev_couchdb.yaml'


# Helmfile deployment requires information on CouchDB configuration
def couchdb_helmfile_values_factory(*, context):
    with open(COUCHDB_CONFIG_PATH) as couchdb_config_file:
        couchdb_config = ruamel.yaml.safe_load(couchdb_config_file)

        return {
            'adminUsername': couchdb_config['admin']['user'],
            'adminPassword': couchdb_config['admin']['password'],
            'cookieAuthSecret': couchdb_config['config']['cookieAuthSecret'],
            'couchdbConfig': {
                'couchdb': {
                    'uuid': couchdb_config['config']['uuid']
                }
            },
        }


# Helmfile deployment requires information on accessing the ECR
def ecr_helmfile_values_factory(*, context):
    with tasks.terraform.ecr.ecr_read_only(context=context) as ecr_read_only:
        return {
            'registryUrl': ecr_read_only.output.registry_url,
            'registryUser': ecr_read_only.output.registry_user,
            'registryPassword': ecr_read_only.output.registry_password,
        }


task_helmfile_migraine_apply = aws_infrastructure.tasks.library.instance_helmfile.task_helmfile_apply(
    config_key=CONFIG_KEY,
    ssh_config_path=SSH_CONFIG_PATH,
    staging_local_dir=STAGING_LOCAL_HELMFILE_DIR,
    staging_remote_dir=STAGING_REMOTE_HELMFILE_DIR,
    helmfile_path=HELMFILE_PATH,
    helmfile_config_path=HELMFILE_CONFIG_PATH,
    helmfile_values_factories={
        'ecr_generated': ecr_helmfile_values_factory,
        'secrets_couchdb_generated': couchdb_helmfile_values_factory,
    },
)
task_helmfile_migraine_apply.__doc__ = 'Apply helmfile/helmfile.yaml in the instance.'


ns = Collection('helmfile')
ns.add_task(task_helmfile_migraine_apply, 'apply')
