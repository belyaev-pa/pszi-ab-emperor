# -*- coding: utf-8 -*-

import ConfigParser
import sqlite3
import json


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


def job_printing(path):
    if path is None:
        raise ConfFileError('В конфигурационном файле АБ отсутствует job_json_conf_path')
    with open(path) as conf:
        json_conf = json.load(conf)
        for item in json_conf.keys():
            print('Job: {} | required aliases {}'.format(item, json_conf[item]['job']['files']['alias']))


def problem_job_flushing(db_path):
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

class ConfFileError(Exception): pass
