# -*- coding: utf-8 -*-
from .lib.daemon import DaemonConfigurator, UnsupportedCommandException
from ab_base_daemon import ABBaseDaemon


def create_daemon(command, conf_dict):
    """
    Функция создания и управлению демоном
    :param command: строка содержащая команду start, stop, restart
    :param conf_dict: словарь с настройками
    :return: void
    """
    daemon = ABBaseDaemon(pidfile=conf_dict['PID_FILE_PATH'],
                          conf_dict=conf_dict,
                          log_name=conf_dict['LOG_NAME'])
    config = DaemonConfigurator(daemon)
    react_dict = config.get_reacts_for_daemon()
    try:
        react_dict[command]()
    except KeyError as e:
        raise UnsupportedCommandException(e)