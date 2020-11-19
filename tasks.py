from invoke import Collection

import terraform_elastic_ip
import terraform_instance

ns = Collection()

ns.add_collection(terraform_elastic_ip.ns, name='elastic-ip')
ns.configure(terraform_elastic_ip.ns.configuration())

ns.add_collection(terraform_instance.ns, name='instance')
ns.configure(terraform_instance.ns.configuration())
