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
        TODO: доделать ветку возврата после сбоя
        TODO: сделать создание pid файла и запись pid процесса в файл
        TODO: добавить + os.remove(JOB_HANDLER_PID_FILE_PATH)
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
            while True:
                data = self.socket_conn.recv(1024)

                if not data:
                    conf = json.loads(data)
                    with JobHandler(conf['job_id'], self.conf_dict) as job:
                        job.run_job()
                    break
