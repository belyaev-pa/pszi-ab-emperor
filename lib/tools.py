# -*- coding: utf-8 -*-

import ConfigParser
import sqlite3
import json
import os


def parse_conf(conf_file_path):
    """
    Функция парсинга конфиг файла
    одноименные ключи будут затерты, будет взят последний
    :param conf_file_path: путь до файла
    :return: сформированный словарь настроек
    """
    config = ConfigParser.ConfigParser()
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
            s = 'Наименование работы: {}, имеет {} необходимый(ых) файл(ов):'.format(
                item, json_conf[item]['job']['files']['count'])
            for alias in json_conf[item]['job']['files']['alias']:
                s += str(' {},'.format(alias))
            print(s.rstrip(','))


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


def validate_job_args(job_type, job_args, json_path):
    with open(json_path) as conf:
        json_conf = json.load(conf)
        job = json_conf.get(job_type, None)
        if job is None:
            raise ABConsoleError('переданной работы нет в конфигурационном файле (ノ_<。)ヾ(´ ▽ )')
    try:
        file_count = int(job['job']['files']['count'])
    except ValueError:
        raise ConfFileError(
            'Количество файлов в конфигурационном файле для работы {} должно быть указано цифрой (＃＞＜)'.format(
                job_type))
    if file_count == 0 and job_args is None:
        return
    elif file_count == 0 and job_args is not None:
        raise ABConsoleError('У переданной работы нет передаваемых ей файлов (＞ｍ＜)')
    elif file_count > 0 and job_args is None:
        raise ABConsoleError('У переданной работы есть {} необходимый(ых) файл(ов) (￣□￣」)'.format(file_count))
    else:
        aliases = list()
        for obj in job_args.split(' '):
            if '=' not in obj:
                raise ABConsoleError('Неверный формат аргумента {} отсутствует "="'.format(obj))
            file_param = obj.split('=')
            aliases.append(file_param[0])
        set_j = set(job['job']['files']['alias'])
        set_a = set(aliases)
        if set_j != set_a:
            msg = 'Переданы неверные аргументы: '
            for obj in set_a.difference(set_j):
                msg += ' {},'.format(obj)
            raise ABConsoleError(msg.rstrip(','))


def conf_view(conf_path):
    print('Список параметров конфигурационного файла:')
    for k, v in parse_conf(conf_path).iteritems():
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


class ConfFileError(Exception): pass


class ABConsoleError(Exception): pass
