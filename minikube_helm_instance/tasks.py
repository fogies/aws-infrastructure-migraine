from invoke import task
import os


@task
def initialize(context):
    """
    Initialize Terraform.
    """

    config = context.config.minikube_helm_instance
    working_dir = os.path.normpath(config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Initializing Terraform')
        context.run(
            ' '.join([
                bin_terraform,
                'init',
                '-no-color'
            ]),
            hide="stdout"
        )


@task(
    pre=[initialize]
)
def create(context):
    """
    Create our Minikube instance.
    """

    config = context.config.minikube_helm_instance
    working_dir = os.path.normpath(config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Creating Minikube Instance')
        context.run(
            ' '.join([
                bin_terraform,
                'apply',
                '-auto-approve -no-color'
            ])
        )


@task(
    pre=[initialize]
)
def destroy(context):
    """
    Destroy our Minikube instance.
    """

    config = context.config.minikube_helm_instance
    working_dir = os.path.normpath(config.working_dir)
    bin_terraform = os.path.normpath(os.path.join(config.bin_dir, 'terraform.exe'))

    with context.cd(working_dir):
        print('Destroying Minikube Instance')
        context.run(
            ' '.join([
                bin_terraform,
                'destroy',
                '-auto-approve -no-color'
            ])
        )
