import click
import yaml
import os
import sys
import pprint
import json
import aio_pika
import asyncio


@click.command()
@click.option('--config', default='config.yml', help='Path to config file')
def config_rmq(config):
    """import yaml config file and creates a dictionary from it"""
    # get the path to the config file
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, config)

    # open the config file and read it
    asyncio.run(create_from_config(path))


if __name__ == '__main__':
    config_rmq()


exchange_type_map = {
    'direct': aio_pika.ExchangeType.DIRECT,
    'topic': aio_pika.ExchangeType.TOPIC,
    'headers': aio_pika.ExchangeType.HEADERS,
    'fanout': aio_pika.ExchangeType.FANOUT
}


async def create_from_config(path):
    # open the config file and read it
    with open(path, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    # connect to the RabbitMQ server
    for _ in range(10):
        # try to connect 10 times
        try:
            vh = cfg['virtualhost'] if cfg['virtualhost'] != '/' else ''
            connection_url = f"amqp://{cfg['username']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{vh}"
            connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
                connection_url,
                client_properties={"client_properties": {
                    "service": "roborabbit"}},
            )
            break
        except ConnectionError:
            # try again
            await asyncio.sleep(3)
        else:
            raise ConnectionError(
                f"Could not connect to rabbit at {cfg.url} "
                f"with username {cfg.username}"
            )
    channel: aio_pika.Channel = await connection.channel()

    # declare the exchanges
    x_conns = {}
    for exchange in cfg['exchanges']:
        ex_type = exchange_type_map[exchange.get('type', 'topic')]
        x_conns[exchange['name']] = await channel.declare_exchange(
            exchange['name'],
            type=ex_type,
            durable=exchange.get('durable', True),
            auto_delete=exchange.get('auto_delete', False)
        )

    # declare the queues
    q_conns = {}
    for queue in cfg['queues']:
        dlq_args = {
            **{"x-queue-type": queue.get("type", "quorum")},
            **queue.get("arguments", {})
        }

        q_conns[queue['name']] = await channel.declare_queue(
            queue['name'],
            arguments=dlq_args,
            durable=queue.get('durable', True),
            robust=queue.get('robust', True),
            auto_delete=queue.get('auto_delete', False),
            exclusive=queue.get('exclusive', False)
        )

    # bind the queues to the exchanges
    for bindings in cfg['bindings']:
        if bindings['from']['type'] == 'queue':
            from_qx = q_conns[bindings['from']['name']]
        elif bindings['from']['type'] == 'exchange':
            from_qx = x_conns[bindings['from']['name']]
        else:
            raise Exception(f"Unknown from type {bindings['from']['type']}")

        if bindings['to']['type'] == 'queue':
            to_qx = q_conns[bindings['to']['name']]
        elif bindings['to']['type'] == 'exchange':
            to_qx = x_conns[bindings['to']['name']]
        else:
            raise Exception(f"Unknown to type {bindings['to']['type']}")

        if bindings.get('bind_options'):
            await to_qx.bind(
                from_qx,
                arguments=bindings.get('bind_options')
            )
        else:
            await to_qx.bind(from_qx, routing_key=bindings['routing_key'])

    # TODO: Create dead letter queues
