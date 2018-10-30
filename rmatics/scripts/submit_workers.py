import click
from gevent import monkey
monkey.patch_all()

from gevent.pool import Group

from rmatics.wsgi import application
from rmatics.ejudge.submit_queue.queue import SubmitQueue
from rmatics.ejudge.submit_queue.worker import SubmitWorker

from rmatics import create_app


@application.cli.command()
@click.option('--workers', default=2)
def main(workers):
    create_app()
    queue = SubmitQueue()
    worker_group = Group()
    for _ in range(workers):
        worker_group.start(SubmitWorker(queue))
    worker_group.join()


if __name__ == '__main__':
    main()
