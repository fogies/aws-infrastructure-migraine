from invoke import Collection

import elastic_ip
import minikube_helm_instance

ns = Collection()

ns.add_collection(elastic_ip.ns, name='elastic-ip')
ns.configure(elastic_ip.ns.configuration())

ns.add_collection(minikube_helm_instance.ns, name='minikube-helm-instance')
ns.configure(minikube_helm_instance.ns.configuration())
