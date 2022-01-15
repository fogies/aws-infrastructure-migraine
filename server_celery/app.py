import celery
import celery.apps.worker
import logging
import tasks

app = celery.Celery('celery')
app.conf.update({
    'broker_url': 'filesystem://localhost//',
    'broker_transport_options': {
        'data_folder_in': './broker/data',
        'data_folder_out': './broker/data',
        'data_folder_processed': './broker/processed'
    },
    'imports': ['tasks'],
    'beat_schedule': {
        'say-hi': {
            'task': 'tasks.celery_ciao',
            'schedule': 15,

        }
    }
})

if __name__ == '__main__':
    app.worker_main(
        argv=[
            'worker',
            '--loglevel=info',
            '--concurrency=1',
            '--pool=gevent',
        ]
    )
