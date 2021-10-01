from pathlib import Path

from roborabbit.logger import logger
from roborabbit.connection import connect
import yaml
import sys
import json
import aio_pika


exchange_type_map = {
    'direct': aio_pika.ExchangeType.DIRECT,
    'topic': aio_pika.ExchangeType.TOPIC,
    'headers': aio_pika.ExchangeType.HEADERS,
    'fanout': aio_pika.ExchangeType.FANOUT
}


async def create_exchanges(exchanges, channel):
    x_conns = {}
    for exchange in exchanges:
        logger.info('Declaring exchange: %s', exchange['name'])
        ex_type = exchange_type_map[exchange.get('type', 'topic')]
        x_conns[exchange['name']] = await channel.declare_exchange(
            exchange['name'],
            type=ex_type,
            durable=exchange.get('durable', True),
            auto_delete=exchange.get('auto_delete', False)
        )
    return x_conns


async def create_queues(queues, channel):
    q_conns = {}
    for queue in queues:
        logger.info('Declaring queue: %s', queue['name'])
        dlx_name = queue.get('dlx', f"{queue['name']}_dlx")
        dlq_name = queue.get('dlq', f"{queue['name']}_dlq")
        q_args = {
            **{"x-queue-type": queue.get("type", "quorum")},
            **queue.get("arguments", {})
        }

        await channel.declare_exchange(
            dlx_name,
            type=aio_pika.ExchangeType.TOPIC,
            durable=True,
            auto_delete=False
        )

        dlq = await channel.declare_queue(
            dlq_name,
            arguments=q_args,
            durable=True,
            robust=True,
            auto_delete=False,
            exclusive=False
        )
        await dlq.bind(dlx_name, routing_key='#')

        q_conns[queue['name']] = await channel.declare_queue(
            queue['name'],
            arguments={"x-dead-letter-exchange": dlx_name, **q_args},
            durable=queue.get('durable', True),
            robust=queue.get('robust', True),
            auto_delete=queue.get('auto_delete', False),
            exclusive=queue.get('exclusive', False)
        )
    return q_conns


async def bind_queues(bindings, x_conns, q_conns):
    for binding in bindings:
        if binding['from']['type'] == 'queue':
            from_qx = q_conns[binding['from']['name']]
        elif binding['from']['type'] == 'exchange':
            from_qx = x_conns[binding['from']['name']]
        else:
            raise Exception(f"Unknown from type {binding['from']['type']}")

        if binding['to']['type'] == 'queue':
            to_qx = q_conns[binding['to']['name']]
        elif binding['to']['type'] == 'exchange':
            to_qx = x_conns[binding['to']['name']]
        else:
            raise Exception(f"Unknown to type {binding['to']['type']}")

        if binding.get('bind_options'):
            for _options in binding.get('bind_options'):
                logger.info(f'Binding {from_qx.name} to {to_qx.name} using {json.dumps(_options)}')
                await to_qx.bind(
                    from_qx,
                    arguments=_options
                )
        else:
            logger.info(f'Binding {from_qx.name} to {to_qx.name} using routing_key "{binding["routing_keys"]}"')
            for _key in binding['routing_keys']:
                await to_qx.bind(from_qx, routing_key=_key)


async def create_from_config(path: Path):
    # open the config file and read it
    try:
        if not isinstance(path, Path):
            raise Exception('Must pass pathlib.Path as path')
        logger.info(f'Config file: {path}')
        with open(path, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    except FileNotFoundError:
        print(f'file not found: {path.absolute()}')
        sys.exit(1)

    # connect to the RabbitMQ server
    connection = await connect(cfg)

    logger.info('Creating channel')
    channel: aio_pika.Channel = await connection.channel()

    # declare the exchanges
    x_conns = await create_exchanges(cfg['exchanges'], channel)

    # declare the queues
    q_conns = await create_queues(cfg['queues'], channel)

    # bind the queues to the exchanges
    await bind_queues(cfg['bindings'], x_conns, q_conns)

    logger.warn('Done!')
    # TODO: Create dead letter queues

    return connection, q_conns
