#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import socket
import sys
import json
import uuid

from ab_dispatcher.tools import parse_conf, job_printing, problem_job_clearing
from ab_dispatcher.tools import db_flush, validate_job_args, conf_view, conf_check


CONF_FILE_PATH = '/etc/ab-dispatcher/ab-dispatcher.conf'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start handling job with provided type')
    parser.add_argument('-t', '--job_type', type=str, dest='job_type', nargs='?',
                        help='Наименование выполняемой работы пример: -t=test_job')
    parser.add_argument('-a', '--args', type=str, dest='job_args', nargs='?',
                        help='строка аргументов пример : -a="alias1=/path/to/file1 alias2=/path/to/file2"')
    parser.add_argument('-i', '--info', dest='job_info', action='store_true',
                        help='Выводит список доступных для выполнения работ с необходимыми аргументами')
    parser.add_argument('-c', '--clear', dest='remove_problem_job', action='store_true',
                        help='Удаляет все задачи с ошибкой выполнения')
    parser.add_argument('--flush', dest='flush_job_db', action='store_true',
                        help='Очищает БД полностью. Будьте предельно аккуратны с этим флагом')
    parser.add_argument('-v', '--view', dest='conf_view', action='store_true',
                        help='Выводит все текущие параметры конфигурационного файла')
    parser.add_argument('-k', '--check', dest='conf_check', action='store_true',
                        help='Проверяет все ли необходимые для работы параметры присутствуют в конфигурацинном файле')
    args = parser.parse_args()
    conf_dict = parse_conf(CONF_FILE_PATH)
    if args.job_info:
        job_printing(conf_dict.get('job_json_conf_path', None))
        sys.exit()
    if args.remove_problem_job:
        problem_job_clearing(conf_dict.get('sqlite3_db_path', None))
        sys.exit()
    if args.flush_job_db:
        db_flush(conf_dict.get('sqlite3_db_path', None))
        sys.exit()
    if args.conf_view:
        conf_view(CONF_FILE_PATH)
        sys.exit()
    if args.conf_check:
        conf_check(CONF_FILE_PATH)
        sys.exit()
    validate_job_args(args.job_type, args.job_args, conf_dict.get('job_json_conf_path', None))
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_address = conf_dict['socket_path']
    message = json.dumps(dict(
        job_id=str(uuid.uuid4()),
        job_type=args.job_type,
        manager_type='local',
        arguments=args.job_args
    ))
    print('Пытаюсь выполнить заданную работу...')
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
    print('Выполнение завершено.')
    print('Лог файл можно посмотреть: {}'.format(answer_received))
