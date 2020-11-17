# Support Invoke discovery of tasks
from .tasks import *

# Collection configured for expected use
from invoke import Collection

ns = Collection()

ns.add_task(create)
ns.add_task(destroy)
ns.add_task(output)

ns.configure({
    'elastic_ip': {
        'working_dir': 'elastic_ip',
        'bin_dir': '../bin'
    }
})

del Collection
