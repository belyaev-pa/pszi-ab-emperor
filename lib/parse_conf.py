# -*- coding: utf-8 -*-

import ConfigParser

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
