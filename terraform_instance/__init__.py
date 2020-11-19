from invoke import Collection

from .tasks import *

# Collection configured for expected use
ns = Collection()

ns.add_task(apply)
ns.add_task(destroy)

ns.configure({
    CONFIG_KEY: {
        'working_dir': 'terraform_instance',
        'bin_dir': '../bin'
    }
})

del Collection

try:
    from . import instance as instance
    ns.add_collection(instance.ns, name='instance')
    ns.configure({
        CONFIG_KEY: instance.ns.configuration()
    })
except (AttributeError, ImportError, SyntaxError):
    pass
