# -*- coding: utf-8 -*-
import json
import socket
from base_db import BaseDB
from job_handler import SingletonMeta, JobHandler


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
        self.socket_path = self.get_settings('SOCKET_PATH')
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
        rows = self.select_db_row("status", "processing")
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
                    if self.select_db_row('job_id', conf['job_id']):
                        # TODO: проверить, если файл лога
                        pass
                        # TODO: сделать ответ, что задача уже выполнена
                    else:
                        with JobHandler(conf['job_id'], self.conf_dict) as job:
                            job.run_job()
                        # TODO: ответить лог файлом
                    break
