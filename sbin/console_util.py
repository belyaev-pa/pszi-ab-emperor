#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import socket
import sys
import json
import uuid
import ConfigParser


CONF_FILE_PATH = '/etc/ab-dispather/ab-dispather.conf'


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start handling job with provided type')
    parser.add_argument('job_type', type=str, help='Job type for handling')
    parser.add_argument('job_args', type=str, help='string with args alias=/path/to/file space separated')
    args = parser.parse_args()
    conf_dict = parse_conf(CONF_FILE_PATH)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_address = conf_dict['socket_path']
    message = json.dumps(dict(
        job_id=str(uuid.uuid4()),
        job_type=args.job_type,
        manager_type='local',
        arguments=args.job_args
    ))
    try:
        sock.connect(server_address)
    except socket.error:
        sys.exit("не могу подключиться к сокету")
    try:
        sock.sendall(message + '\r\n\r\n')
        answer_received = ''
        while not answer_received.endswith('\r\n\r\n'):
            data = sock.recv(32)
            answer_received += data
    finally:
        sock.close()
    print('log is here: {}'.format(answer_received))
