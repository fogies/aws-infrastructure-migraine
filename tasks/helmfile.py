import aws_infrastructure.tasks.library.instance_helmfile
from invoke import Collection
import ruamel.yaml
from pathlib import Path

import migraine_shared.config
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

DEV_COUCHDB_CONFIG_PATH = "./secrets/configuration/dev_couchdb.yaml"
PROD_COUCHDB_CONFIG_PATH = "./secrets/configuration/prod_couchdb.yaml"
PROD_FLASK_CONFIG_PATH = "./secrets/configuration/prod_flask.yaml"

# Helmfile deployment requires information on CouchDB development configuration
def couchdb_dev_helmfile_values_factory(*, context):
    couchdb_config = migraine_shared.config.CouchDBConfig.load(couchdb_config_path=DEV_COUCHDB_CONFIG_PATH)

    return {
        'adminUsername': couchdb_config.admin_user,
        'adminPassword': couchdb_config.admin_password,
        'cookieAuthSecret': couchdb_config.cookie_auth_secret,
        'couchdbConfig': {
            'couchdb': {
                'uuid': couchdb_config.uuid
            }
        },
    }


# Helmfile deployment requires information on CouchDB production configuration
def couchdb_prod_helmfile_values_factory(*, context):
    couchdb_config = migraine_shared.config.CouchDBConfig.load(couchdb_config_path=PROD_COUCHDB_CONFIG_PATH)

    return {
        'adminUsername': couchdb_config.admin_user,
        'adminPassword': couchdb_config.admin_password,
        'cookieAuthSecret': couchdb_config.cookie_auth_secret,
        'couchdbConfig': {
            'couchdb': {
                'uuid': couchdb_config.uuid
            }
        },
    }


# Helmfile deployment requires information on Flask production configuration
def flask_prod_helmfile_values_factory(*, context):
    flask_config = migraine_shared.config.FlaskConfig.load(flask_config_path=PROD_FLASK_CONFIG_PATH)

    return {
        'flask': {
            'baseurl': flask_config.baseurl,
            'secret_key': flask_config.secret_key,
            'database_url': flask_config.database_baseurl,
            'database_admin': {
                'user': flask_config.database_admin_user,
                'password': flask_config.database_admin_password,
            }
        }
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
        'secrets_couchdb_dev_generated': couchdb_dev_helmfile_values_factory,
        'secrets_couchdb_prod_generated': couchdb_prod_helmfile_values_factory,
        'secrets_flask_prod_generated': flask_prod_helmfile_values_factory,
    },
)
task_helmfile_migraine_apply.__doc__ = 'Apply helmfile/helmfile.yaml in the instance.'


ns = Collection('helmfile')
ns.add_task(task_helmfile_migraine_apply, 'apply')
