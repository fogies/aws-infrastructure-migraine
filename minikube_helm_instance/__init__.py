# Support Invoke discovery of tasks
from .tasks import *

# Collection configured for expected use
from invoke import Collection

ns = Collection()

ns.add_task(create)
ns.add_task(destroy)

ns.configure({
    'minikube_helm_instance': {
        'working_dir': 'minikube_helm_instance',
        'bin_dir': '../bin'
    }
})

del Collection

try:
    from . import instance as instance
    ns.add_collection(instance.ns, name='instance')
    ns.configure({
        'minikube_helm_instance': instance.ns.configuration()
    })
except (AttributeError, ImportError, SyntaxError):
    pass
