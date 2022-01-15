import celery


print('loading')


@celery.shared_task()
def celery_hello():
    print("Hello")


@celery.shared_task()
def celery_hola():
    print("Hola")

    celery_hello.apply_async()
    celery_hello.apply_async()
    celery_hello.apply_async()
    celery_hello.apply_async()
    celery_hello.apply_async()


@celery.shared_task()
def celery_ciao():
    print("Ciao")

    celery_hola.apply_async()
    celery_hola.apply_async()
    celery_hola.apply_async()
    celery_hola.apply_async()
    celery_hola.apply_async()
