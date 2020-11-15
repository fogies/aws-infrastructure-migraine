from invoke import Collection

import elastic_ip

ns = Collection()

ns.add_collection(elastic_ip.ns, name='elastic-ip')
ns.configure(elastic_ip.ns.configuration())
