#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from python_sz_daemon.daemon_configurator  import DaemonConfigurator
from ab_dispatcher.ab_base_daemon import ABBaseDaemon
from ab_dispatcher.parse_conf import parse_conf


CONFIG_PATH = '/etc/ab-dispatcher/ab-dispatcher.conf'


def create_daemon(command, conf_dict):
    """
    Функция создания и управлению демоном
    :param command: строка содержащая команду start, stop, restart
    :param conf_dict: словарь с настройками
    :return: void
    """
    daemon = ABBaseDaemon(pidfile=conf_dict['pid_file_path'],
                          conf_dict=conf_dict,
                          log_name=conf_dict['log_name'])
    config = DaemonConfigurator(daemon)
    react_dict = config.get_reacts_for_daemon()
    try:
        react_dict[command]()
    except KeyError as e:
        raise KeyError('Such "{}" command can not be found'.format(command))


if __name__ == '__main__':
    conf = parse_conf(CONFIG_PATH)
    if len(sys.argv) > 1:
        create_daemon(sys.argv[1], conf)
        sys.exit(0)
    else:
        print("Usage {} without arguments is prohibited".format(sys.argv[0]))
        sys.exit(2)
