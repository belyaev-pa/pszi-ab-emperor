# -*- coding: utf-8 -*-
import json
import os
import socket
from datetime import datetime
from collections import namedtuple

from ab_dispather.base_db import BaseDB
from ab_dispather.job_handler import SingletonMeta, JobHandler


class ABSocketListener(BaseDB):

    __metaclass__ = SingletonMeta

    def __init__(self, conf_dict):
        """
        Конструктор обработчика заданий
        :param job_id: id задачи из БД, которую нужно выполнить
        :param conf_dict: словарь с настройками
        :param arguments: список аргументов, файлы и пути к ним: ['log_txt_file=/home/pavel/test_log.txt']
        :param manager_type: тип меджера, который запустил функцию (net или local)
        """
        self.conf_dict = conf_dict
        super(ABSocketListener, self).__init__(self.conf_dict)
        self.socket_path = self.get_settings('socket_path')
        self.init_check()
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.socket_path)
        self.sock.listen(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(ABSocketListener, self).__exit__(exc_type, exc_val, exc_tb)
        if self.socket_conn:
            self.socket_conn.close()

    def init_check(self):
        """
        Проверяет незавершенные работы при инициализации
        :return:
        """
        rows = self.select_db_row("status", 1)
        if rows:
            for row in rows:
                with JobHandler(row['job_id'], self.conf_dict) as job:
                    job.run_job()

    def run(self):
        """
        запускает функцию прослушки сокета
        """
        while True:
            self.socket_conn, self.client_address = self.sock.accept()
            received_data = ''
            while True:
                data = self.socket_conn.recv(128)
                received_data += data.decode('utf8').replace("'", '"')
                if received_data.endswith('\r\n\r\n'):
                    conf = json.loads(received_data)
                        # если задача есть в БД, пытаемся отдать файл логов с таким айди,
                        # если есть, если нет файла просто говорим, что задача выполнена
                    log_path = os.path.join(self.get_settings('log_files_dir'), conf['job_id'] + '.log')
                    if self.select_db_row('job_id', conf['job_id']):
                        if os.path.isfile(log_path):
                            self.socket_conn.sendall(log_path + '\r\n\r\n')
                        else:
                            self.socket_conn.sendall('\r\n\r\n')
                    else:
                        self.prepare_job(conf)
                        self.socket_conn.sendall(log_path + '\r\n\r\n')
                    break

    def prepare_job(self, sock_msg):
        """
        функция подготовки к запуску задачи
        :param sock_msg: словарь с необходимыми параметрыми, передаваемым через сокет
        :return:
        """
        DBRow = namedtuple('DBRow', [
            'job_id',
            'status',
            'error',
            'step_number',
            'arguments',
            'task_type',
            'manager_type',
            'completed_steps',
            'date_start',
            'date_finish'
        ])
        db_row = DBRow(job_id=sock_msg['job_id'],
                       status=1,
                       error=0,
                       step_number='step_1',
                       arguments=' '.join(map(str, sock_msg['arguments'])),
                       task_type=sock_msg['task_type'],
                       manager_type=sock_msg['manager_type'],
                       completed_steps='',
                       date_start=datetime.now().strftime(self.get_settings('date_format')),
                       date_finish='',)
        self.insert_into_table(db_row)
        with JobHandler(sock_msg['job_id'], self.conf_dict) as job:
            job.run_job()
