import click
import os
import asyncio
from roborabbit.rmq import create_from_config


@click.command()
@click.option('--config', default='config.yml', help='Path to rabbit config yaml file')
@click.option('--host', help='RabbitMQ host')
@click.option('--port', help='RabbitMQ port')
@click.option('--virtualhost', help='RabbitMQ virtualhost')
@click.option('--username', help='RabbitMQ username')
@click.option('--password', help='RabbitMQ password')
def main(config=None, host=None, port=None, virtualhost=None, username=None, password=None):
    """import yaml config file and creates a dictionary from it"""
    # get the path to the config file
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.join(path, config)

    if host:
        os.environ['RABBIT_HOST'] = host
    if port:
        os.environ['RABBIT_PORT'] = port
    if virtualhost:
        os.environ['RABBIT_VHOST'] = virtualhost
    if username:
        os.environ['RABBIT_USER'] = username
    if password:
        os.environ['RABBIT_PASS'] = password

    # open the config file and read it
    asyncio.run(create_from_config(path))


if __name__ == '__main__':
    main()
