# RoboRabbit

Set up your rabbit instance using a declarative yaml file.

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
# Connection info
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
    routing_key: records.created
```

### Header exchange declaration and binding

```
# Connection info
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
      x-match: all
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
    routing_key: string # required, unless bind_options is defined
    bind_options: # required if binding to a header exchange
      x-match: all|any # header type of matcher
      header-key: string # header topic to be matched
```
