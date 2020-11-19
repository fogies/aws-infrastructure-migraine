from invoke import Collection

from .tasks import *

# Collection configured for expected use
ns = Collection()

ns.add_task(apply)
ns.add_task(destroy)
ns.add_task(output)

ns.configure({
    CONFIG_KEY: {
        'working_dir': 'terraform_elastic_ip',
        'bin_dir': '../bin'
    }
})

del Collection
