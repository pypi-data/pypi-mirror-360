"""
Ehdtd daemon - Daemon script for ehdtd package

Author: Ricardo Marcelo Alvarez
Date: 2024-03-14

"""

import sys
import os
import signal
import time
import datetime # pylint: disable=unused-import
import getopt
import logging
import pprint # pylint: disable=unused-import
from ehdtd import Ehdtd # pylint: disable=unused-import
import ehdtd_daemon.aux_common_functions as acf # pylint: disable=import-error, no-name-in-module

DAEMON_RUNNING = None

def main():
    """
    Main function of the ehdtd_daemon.py.
    =====================================

    This function start and stop daemon.

    Usage:
        python ehdtd_daemon.py [options] command

    Options:
        -h, --help                  Display this help message and exit.
        -c, --config=CONFIG_FILE    Specify alternative config file,\
            Default /etc/ehdtd-daemon/ehdtd-daemon.yaml.
            The ehdtd-daemon.yaml configuration file follows a YAML\
            (YAML Ain't Markup Language) format. It consists of several sections and parameters,\
            allowing customization of the daemon's behavior. See README.md for the format details.

    Commands:
        start       Start the daemon
        stop        Stop the daemon
        check   Check exchange connectivity

    """

    result = 0
    global DAEMON_RUNNING # pylint: disable=global-statement

    argv = sys.argv[1:]

    config_file = '/etc/ehdtd-daemon/ehdtd-daemon.yaml'

    self_script_name = os.path.basename(__file__).split(".")[0]
    command_input = None

    print_help_msg = False

    help_msg = f"""
    Usage: {os.path.basename(__file__)} [OPTIONS] COMMAND

    Options:
        -h, --help                  Display this help message and exit.
        -c, --config=CONFIG_FILE    Specify the config file .

    Commands:
        start   Start the daemon
        stop    Stop the daemon
        check   Check exchange connectivity

    """

    try:
        optlist, args = getopt.getopt(argv, 'hc:', ['help', 'config='])
    except getopt.GetoptError:
        print(help_msg, flush=True)
        return 2

    for opts, arg in optlist:
        if opts in ("-h", "--help"):
            print_help_msg = True
        elif opts in ("-c", "--config"):
            config_file = arg

    if args is not None and isinstance(args, list) and len(args) > 0:
        command_input = args[0]

    if print_help_msg:
        print(help_msg, flush=True)
        return 0

    config_data = acf.get_config_data(config_file)

    if config_data is None:
        err_msg = 'Inexistent or bad config file.'
        print(err_msg, flush=True)
        return 2

    db_type = None
    db_host = None
    db_port = None
    db_name = None
    db_user = None
    db_pass = None

    if 'db_data' in config_data:
        db_data = config_data['db_data']

        if 'db_type' in db_data:
            db_type = db_data['db_type']

        if 'db_host' in db_data:
            db_host = db_data['db_host']

        if 'db_port' in db_data:
            db_port = db_data['db_port']

        if 'db_name' in db_data:
            db_name = db_data['db_name']

        if 'db_user' in db_data:
            db_user = db_data['db_user']

        if 'db_pass' in db_data:
            db_pass = db_data['db_pass']

    if not acf.check_database_connection(db_type, db_host, db_port, db_name, db_user, db_pass):
        print('Database connection ERROR')
        return 2

    log_dir = config_data['global']['log_dir']
    run_dir = config_data['global']['run_dir']

    restart_time_limit = config_data.get('global', {}).get('restart_time_limit', 14400)

    run_file = os.path.join(run_dir, "ehdtd-daemon.pid")
    log_file = os.path.join(log_dir, "ehdtd-daemon.log")
    err_file = os.path.join(log_dir, "ehdtd-daemon.err")

    connections_ok = True
    connections_data = {}

    if config_data is not None\
        and 'exchanges' in config_data\
        and config_data['exchanges'] is not None\
        and isinstance(config_data['exchanges'], dict):
        for exchange in config_data['exchanges']:
            if exchange is not None and isinstance(exchange, str):
                connection_data = Ehdtd.get_exchange_connectivity(exchange)
                connection_data_out = {}
                connection_data_out['result'] = None
                connection_data_out['code'] = None
                connection_data_out['res_code'] = None
                connection_data_out['res_msg'] = None
                if connection_data is not None and isinstance(connection_data, dict):
                    if 'result' in connection_data:
                        connection_data_out['result'] = connection_data['result']

                    if 'code' in connection_data:
                        connection_data_out['code'] = connection_data['code']

                    if 'res_code' in connection_data:
                        connection_data_out['res_code'] = connection_data['res_code']

                    if 'res_msg' in connection_data:
                        connection_data_out['res_msg'] = connection_data['res_msg']

                connections_data[exchange] = connection_data_out
                if connections_data[exchange] is None or not connections_data[exchange]['result']:
                    connections_ok = False
    else:
        connections_ok = False

    if command_input == "start":
        if not connections_ok:
            err_msg = pprint.pformat(connections_data, sort_dicts=False)
            print('Connection error:')
            print(err_msg)
            return 1

        def capture_signal(signal_number, frame): # pylint: disable=unused-argument
            global DAEMON_RUNNING # pylint: disable=global-statement
            result = True
            DAEMON_RUNNING = False # pylint: disable=unused-variable
            return result

        signal.signal(signal.SIGTERM, capture_signal)
        signal.signal(signal.SIGINT, capture_signal)

        command_pid = os.fork()

        if command_pid == 0:
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)

            __log_formatter = (
                logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S -')
            )

            __err_formatter = (
                logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S -')
            )

            log_handler = logging.handlers.WatchedFileHandler(log_file)
            log_handler.setFormatter(__log_formatter)
            __local_log_logger = logging.getLogger('EHDTD_DAEMON_LOG')
            __local_log_logger.setLevel(logging.INFO)

            for handler in __local_log_logger.handlers[:]:
                __local_log_logger.removeHandler(handler)

            __local_log_logger.addHandler(log_handler)

            err_handler = logging.handlers.WatchedFileHandler(err_file)
            err_handler.setFormatter(__err_formatter)
            __local_err_logger = logging.getLogger('EHDTD_DAEMON_ERR')
            __local_err_logger.setLevel(logging.ERROR)

            for handler in __local_err_logger.handlers[:]:
                __local_err_logger.removeHandler(handler)

            __local_err_logger.addHandler(err_handler)

            log_msg = f'Starting {self_script_name}'
            __local_log_logger.info(log_msg)
            daemon_pid = os.getpid()
            acf.file_put_contents(run_file, str(daemon_pid) + '\n')

            ehds = []
            end_log_msg = None

            try:
                for exchange, data in config_data['exchanges'].items():
                    ehd = None
                    ehd = Ehdtd(exchange,\
                                data['fetch_data'],\
                                config_data['db_data'],\
                                log_dir=log_dir,\
                                trading_type=data['trading_type'],\
                                debug=config_data['global']['debug'])
                    ehds.append(ehd)
                    DAEMON_RUNNING = False

                end_log_msg = f'Stopping {self_script_name}'

            except Exception as exc: # pylint: disable=broad-except
                err_msg = f'Error on starting daemon -> {exc}'
                __local_err_logger.error(err_msg)
                DAEMON_RUNNING = False
            else:
                DAEMON_RUNNING = False
                end_log_msg = f'Stopping {self_script_name}'

            if ehds is not None and isinstance(ehds, list) and len(ehds) > 0:
                for ehd in ehds:
                    if ehd is not None:
                        ehd.start()
                DAEMON_RUNNING = True

            __time_end = time.time() + restart_time_limit

            while DAEMON_RUNNING:
                if time.time() > __time_end:
                    if ehds is not None and isinstance(ehds, list) and len(ehds) > 0:
                        for ehd in ehds:
                            if ehd is not None:
                                ehd.stop()
                                time.sleep(1)
                                ehd.start()

                    __time_end = time.time() + restart_time_limit

                time.sleep(5)

            if ehds is not None and isinstance(ehds, list) and len(ehds) > 0:
                for ehd in ehds:
                    if ehd is not None:
                        ehd.stop()

            if end_log_msg is not None:
                __local_log_logger.info(end_log_msg)

            if os.path.exists(run_file):
                os.remove(run_file)

        else:
            log_msg = f'Starting {self_script_name} ... '
            print(log_msg, end='', flush=True)
            time.sleep(1)
            print('Ready', flush=True)
            return 0

    elif command_input == "stop":
        result = 0
        log_msg = f'Stopping {self_script_name} ...'
        print(log_msg, end='', flush=True)
        check_pid = os.getpid()

        pid_to_kill = None

        if os.path.exists(run_file):
            pid_to_kill = int(acf.file_get_contents(run_file))
        else:
            if not connections_ok:
                err_msg = pprint.pformat(connections_data, sort_dicts=False)
                print('Connection error:')
                print(err_msg)
                return 1

        if pid_to_kill is not None and pid_to_kill != check_pid and acf.is_pid_running(pid_to_kill):
            os.kill(pid_to_kill,signal.SIGTERM)

        max_wait_to_stop = 900
        time_stop = 0

        while acf.is_pid_running(pid_to_kill) and time_stop <= max_wait_to_stop:
            time_stop += 1
            print('.', end='', flush=True)
            time.sleep(5)

        if acf.is_pid_running(pid_to_kill):
            os.kill(pid_to_kill,signal.SIGKILL)
            result = 1
        print(' Ready', flush=True)

    elif command_input == "check":
        out_msg = pprint.pformat(connections_data, sort_dicts=False)
        print(out_msg)
        return 0

    return result

if __name__ == "__main__":
    main()
