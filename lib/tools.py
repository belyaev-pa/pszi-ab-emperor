# -*- coding: utf-8 -*-

import configparser
import sqlite3
import json
import os
import sys
import itertools


def parse_conf(conf_file_path):
    """
    Функция парсинга конфиг файла
    одноименные ключи будут затерты, будет взят последний
    :param conf_file_path: путь до файла
    :return: сформированный словарь настроек
    """
    config = configparser.ConfigParser()
    config.read(conf_file_path)
    config_dict = dict()
    for section in config.sections():
        section_dict = {key: value for (key, value) in config.items(section)}
        config_dict.update(section_dict)
    return config_dict


def job_printing(json_path):
    if json_path is None:
        raise ConfFileError('В конфигурационном файле АБ отсутствует job_json_conf_path')
    with open(json_path) as conf:
        json_conf = json.load(conf)
        for item in json_conf.keys():
            print('*' * 50)
            print('Наименование работы: {},'.format(item))
            print(', имеет {} необходимый(ых) файл(ов) с алиасами:'.format(json_conf[item]['job']['files']['count']))
            print(','.join([alias for alias in json_conf[item]['job']['files']['alias']]).rstrip(','))
            print(', имеет {} необходимый(ых) именованый(ых) агрумент(ов) с алиасами:'.format(
                json_conf[item]['job']['files']['count']))
            print(', '.join([alias for alias in json_conf[item]['job']['kwargs']['alias']]).rstrip(','))
        else:
            print('*' * 50)


def problem_job_clearing(db_path):
    if db_path is None:
        raise ConfFileError('В конфигурационном файле АБ отсутствует sqlite3_db_path')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
                DELETE
                FROM ab_tasks
                WHERE error=1;
                """)
    c.close()
    conn.commit()
    conn.close()


def db_flush(db_path):
    if os.path.isfile(db_path):
        os.remove(db_path)


def validate_job(job_type, args, json_path, validate_type):
    """
    функция занимается валидацией именованых агрументов и файлов
    :param job_type: наименование работы
    :param args: агрументы или файлы
    :param json_path: путь до json файла
    :param validate_type: тип валидирования 'files' или 'kwargs'
    :return:
    """
    with open(json_path) as conf:
        json_conf = json.load(conf)
        job = json_conf.get(job_type, None)
        if job is None:
            raise ABConsoleError('переданной работы нет в конфигурационном файле')
    try:
        arg_count = int(job['job'][validate_type]['count'])
    except ValueError:
        raise ConfFileError(
            'Количество файлов и агрументов в конфигурационном файле для работы {} должно быть указано цифрой'.format(
                job_type))
    if arg_count == 0 and args is None:
        return
    elif arg_count == 0 and args is not None:
        raise ABConsoleError('У переданной работы нет передаваемых ей файлов или агрументов')
    elif arg_count > 0 and args is None:
        raise ABConsoleError('У переданной работы есть {} необходимый(ых) файл(ов) или агрумент(ов)'.format(arg_count))
    else:
        aliases = list()
        for obj in args.split(' '):
            if '=' not in obj:
                raise ABConsoleError('Неверный формат аргумента или файлов {} отсутствует "="'.format(obj))
            file_param = obj.split('=')
            aliases.append(file_param[0])
        set_j = set(job['job'][validate_type]['alias'])
        set_a = set(aliases)
        if set_j != set_a:
            msg = 'Переданы неверные аргументы: '
            for obj in set_a.difference(set_j):
                msg += ' {},'.format(obj)
            raise ABConsoleError(msg.rstrip(','))


def conf_view(conf_path):
    print('Список параметров конфигурационного файла:')
    for k, v in parse_conf(conf_path).items():
        print('{} = {}'.format(k, v))


def conf_check(conf_path):
    required_param = {'pid_file_path',
                      'log_name',
                      'sqlite3_db_path',
                      'log_files_dir',
                      'job_json_conf_path',
                      'date_format',
                      'socket_path',
                      'log_files_dir'}
    conf_param = set(parse_conf(conf_path).keys())
    if required_param.issubset(conf_param):
        print('CONF - ОК. Все необходимые параметры присутствуют в файле')
    else:
        msg = 'CONF - НЕ ОК.Некоторые параметры отсутствуют: '
        for obj in required_param.difference(conf_param):
            msg += ' {},'.format(obj)
        print(msg.rstrip(','))


def spin(msg, done):
    write, flush = sys.stdout.write, sys.stdout.flush
    for char in itertools.cycle('|/-\\'):
        status = char + ' ' + msg
        write(status)
        flush()
        write('\x08' * len(status))
        if done.wait(.1):
            break
    write(' ' * len(status) + '\x08' * len(status))


class ConfFileError(Exception): pass


class ABConsoleError(Exception): pass
