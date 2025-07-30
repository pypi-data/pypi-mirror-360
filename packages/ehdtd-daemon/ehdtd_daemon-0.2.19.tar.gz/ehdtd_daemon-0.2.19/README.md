
# ehdtd-daemon

Daemon script for the [ehdtd](https://github.com/rmalvarezkai/ehdtd) package

## Introduction

The ehdtd-daemon is a Python script designed to collect historic and current data from exchanges and store it into a database (PostgreSQL or MySQL). It works in conjunction with the ehdtd package.

## Installation

```bash
pip install --upgrade pip setuptools # This line is only necesary in some setups
pip install ehdtd_daemon
```

## Usage

```python
python ehdtd_daemon.py [options] command
```

## Example

```python
python ehdtd_daemon.py start
sleep 900
python ehdtd_daemon.py stop
```

## Options

* `-h, --help`:                  Display this help message and exit.
* `-c, --config=CONFIG_FILE`:    Specify an alternative config file, Default is '/etc/ehdtd-daemon/ehdtd-daemon.yaml'

## Commands

* `start`:       Start the daemon
* `stop`:        Stop the daemon

## Configuration File Format

The ehdtd-daemon.yaml configuration file follows a YAML (YAML Ain't Markup Language) format. It consists of several sections and parameters, allowing customization of the daemon's behavior.

### Global Configuration

The global configuration section defines settings that apply to the entire daemon operation.

#### Global Parameters

```yaml
log_dir: The directory path for log files. Default is /var/log/ehdtd-daemon.
run_dir: The directory path for runtime files. Default is /run/ehdtd-daemon.
debug: A boolean flag indicating whether to enable debug mode. Default is false.
```

### Database Configuration

The database configuration section defines parameters for connecting to the database.

#### Database Parameters

```yaml
db_type: The type of database used by the daemon. Supported options are postgresql, pgsql and mysql.
db_name: The name of the database.
db_user: The username used to connect to the database.
db_pass: The password used to authenticate the database user.
db_host: The hostname or IP address of the database server.
db_port: The port number on which the database server is listening.
```

### Exchange Configuration

The exchange configuration section defines parameters specific to each supported exchange.

#### Exchange Parameters

```yaml
trading_type: The type of trading supported by the exchange. Currently, only SPOT trading is supported.
fetch_data: A list of dictionaries, each specifying the symbol and interval for fetching data from the exchange.
```

##### Fetch Data Parameters

```yaml
symbol: The trading pair symbol.
interval: The time interval for fetching data, such as 1m for 1 minute or 5m for 5 minutes.
```

### Example Configuration

```yaml

global:
  log_dir: /var/log/ehdtd-daemon
  run_dir: /run/ehdtd-daemon
  debug: false

db_data:
  db_type: postgresql
  db_name: 'DB_NAME'
  db_user: 'DB_USER'
  db_pass: 'DB_PASS'
  db_host: 'DB_HOST'
  db_port: 'DB_PORT'

exchanges:
  binance:
    trading_type: SPOT

    fetch_data:
      - symbol: BTC/USDT
        interval: '1m'
      - symbol: BNB/USDT
        interval: '1m'
      - symbol: ETH/USDT
        interval: '1m'
      - symbol: LTC/USDT
        interval: '1m'
      - symbol: BTC/USDT
        interval: '5m'
      - symbol: BNB/USDT
        interval: '5m'
      - symbol: ETH/USDT
        interval: '5m'
      - symbol: LTC/USDT
        interval: '5m'
```
