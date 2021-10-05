# RoboRabbit
## Main features
- An extremely simple worker class. (!!!!)
- Set up your rabbit queues, exchanges, and bindings using a _declarative_ yaml configuration file.
- Command line interface for bootstrapping rabbit from your roborabbit yaml config file.


## Worker

The simplest worker possible. Connection information is in the `roborabbit.yaml` file. The method `run()` takes an dictionary with a key/value pair:
- key: `queue` - string, the name of the queue to listen to
- value: `handler` - function, the callback function messages will be sent to

### Basic Example
```py
from roborabbit.roborabbit import RoboRabbit
from pathlib import Path

config_path = Path('roborabbit.yaml')
robo = RoboRabbit(config_path)

async def queue_handler(msg):
    print(msg)  # your logic here

await robo.run({'queue_1', queue_handler})
```

### Explicit connection example

If you want control over the configuration, you can pass in the roborabbit connection object.

```py
from roborabbit.connection import Connection
from roborabbit.roborabbit import RoboRabbit
from pathlib import Path

config_path = Path('roborabbit.yaml')
connection = Connection(
    host='not.localhost.com',
    username='bob',
    password='pas123',
    port=4499,
    virtualhost='/')

robo = RoboRabbit(config_path, connection)

async def queue_handler(msg):
    print(msg)  # your logic here

async def work():
    await robo.run({'queue_1', queue_handler})
```

## Command

`roborabbit --config path/to/roborabbit.yaml`

### info

```
Usage: roborabbit [OPTIONS]

  import yaml config file and creates a dictionary from it

Options:
  --config TEXT       Path to rabbit config yaml file
  --host TEXT         RabbitMQ host
  --port TEXT         RabbitMQ port
  --virtualhost TEXT  RabbitMQ virtualhost
  --username TEXT     RabbitMQ username
  --password TEXT     RabbitMQ password
  --help              Show this message and exit.
```

## Override environment variables

```
RABBIT_USER=guest
RABBIT_PASS=guest
RABBIT_HOST=localhost
RABBIT_PORT=5672
RABBIT_VHOST=/
```

## Example yaml files

### Simple declare queue, exchange, and bind

```
host: localhost
username: guest
password: guest
virtualhost: /
port: 5672
exchanges:
  - name: exchange_1
    type: topic
queues:
  - name: queue_1
bindings:
  - from:
      type: exchange
      name: exchange_1
    to:
      type: queue
      name: queue_1
    routing_keys:
      - records.created
```

### Header exchange declaration and binding

```
host: localhost
username: guest
password: guest
virtualhost: /
port: 5672
exchanges:
  - name: exchange_2
    type: headers
queues:
  - name: queue_2
bindings:
  - from:
      type: exchange
      name: exchange_2
    to:
      type: queue
      name: queue_1
    bind_options:
      - x-match: all
        hw-action: header-value
```

## All Values Available

```
# Connection info
host: localhost
username: guest
password: guest
virtualhost: /
port: 5672

# Exchange declarations
exchanges:
  - name: string
    type: topic|headers|direct|fanout # topic is default
    durable: false # default
    auto_delete: true # default

# queue declarations
queues:
  - name: string
    type: quorum # Not required. This is the default and currently only option available (For us, all our queues are quorum. We manually create the queue that needs other requirements). MR welcome
    # create_dlq: true # TODO: This will be the default. Set to false if you do not want a dead letter queue/exchange for this queue
    durable: true # default
    robust: true # default
    auto_delete: false # default
    exclusive: false # default
    auto_delete_delay: 0 # default
    arguments: # rabbit specific key/value pairs
      key_1: value_1
      key_2: value_2

# bindings
bindings:
  - from:
      type: exchange
      name: string
    to:
      type: exchange|queue
      name: string
    routing_keys:
      - record.created  # list of string, required, unless bind_options is defined
    bind_options: # list of `x-match` and `header-key`, required if binding to a header exchange
      - x-match: all|any # header type of matcher
        header-key: string # header topic to be matched
```
