# -*- coding: utf-8 -*-
import os
import json
import subprocess
import re
import syslog
from datetime import datetime
from collections import OrderedDict

from ab_dispatcher.base_db import BaseDB


class JobHandler(BaseDB):
    """
    Класс необходимо создавать через контекстный менеджер, для его корректного завершения!
    """

    def __init__(self, job_id, conf_dict):
        """
        Конструктор обработчика заданий
        :param job_id: id задачи из БД, которую нужно выполнить
        :param conf_dict: словарь с настройками
        """
        self.job_id = job_id
        super(JobHandler, self).__init__(conf_dict)
        self.log_file_path = os.path.join(self.get_settings('log_files_dir'), self.job_id+'.log')
        self.log_file = open(self.log_file_path, 'a')
        syslog.openlog(self.get_settings('log_name'))
        self.job_handling_error = self.get_job_handling_error
        self.job_type = self.get_job_type
        self.job_files = self.make_job_param_dict('arguments')
        self.job_kwargs = self.make_job_param_dict('kwargs')
        self.completed_step = self.get_completed_steps()
        with open(self.get_settings('job_json_conf_path')) as conf:
            json_conf = json.load(conf)
            self.job = json_conf.get(self.job_type, None)
            key = self.job.get('job', None).get('handling', None)
            self.dict_steps = OrderedDict(key)
        if self.job is None or key is None:
            msg = "Wrong handling json file format in section: {0}, {1}\n".format(self.job_id, self.job_type)
            self.write_log(msg)
            # raise WrongJsonFormatException(msg)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.job_handling_error:
            self.update_db_column('error', 1, 'job_id', self.job_id)
            self.make_system_reverse()
        super(JobHandler, self).__exit__(exc_type, exc_val, exc_tb)
        self.log_file.close()
        syslog.closelog()

    def run_job(self):
        """
        вызывает job_handler для каждого шага
        парсим дату
        date_time_obj = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")
        :return:
        """
        msg = "{} : Запускаем выполнение задачи id='{}', type='{}'\n".format(datetime.now(), self.job_id, self.job_type)
        self.write_log(msg)
        if int(self.job['job']['files']['count']) != len(self.job_files.keys()) or \
                int(self.job['job']['kwargs']['count']) != len(self.job_kwargs.keys()):
            msg = "Кол-во файлов или аргументов пререданных не совпадает с количеством файлов " \
                  "или агрументов в конфиге: {0}\n".format(self.job_type)
            self.write_log(msg)
            return self.log_file_path

        for step_number, cmd in self.dict_steps.iteritems():
            if step_number not in self.completed_step:
                if self.job_handler(step_number, self.dict_steps):
                    self.job_handling_error = True
                    msg = "Команда '{}' завершилась не успешно, пытаемся восстановиться\n".format(cmd)
                    self.write_log(msg)
                    break
                self.update_db_column('step_number',
                                      step_number,
                                      'job_id',
                                      self.job_id)
                self.completed_step.append(step_number)
                self.update_db_column('completed_steps',
                                      ' '.join(self.completed_step),
                                      'job_id',
                                      self.job_id)
                msg = "Команда '{}' завершена успешно\n".format(cmd)
                self.write_log(msg)
        else:
            self.update_db_column('status', 0, 'job_id', self.job_id)
            self.update_db_column('date_finish',
                                  datetime.now().strftime(self.get_settings('date_format')),
                                  'job_id',
                                  self.job_id)
            msg = "Задача '{}' выполнена успешно\n".format(self.job_id)
            self.write_log(msg)
        return self.log_file_path

    def job_handler(self, current_step, steps_dict):
        """
        выполняет работу для текущего шага
        необходимо вызвать для каждого шага
        :return:  void
        """
        # current_step = self.select_db_column('step_number', 'job_id', self.job_id)[0]['step_number']
        step_cmd = steps_dict.get(current_step, None)
        if step_cmd is None:
            self.job_handling_error = True
            msg = "переданная команда отсутствует в json: {0}\n".format(self.job_type)
            self.write_log(msg)
            return self.log_file_path
            # raise WrongJsonFormatException()
        new_cmd = self.param_in_cmd_inject(step_cmd)
        process = subprocess.Popen(new_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline, b''):
            print(line.strip())
        return process.wait()
        # TODO: write this into log
        # for line in iter(process.stdout.readline, b''):
        #     print(line.strip())

    def get_completed_steps(self):
        completed_steps = self.select_db_column('completed_steps', 'job_id', self.job_id)[0]['completed_steps']
        return completed_steps.split()

    @staticmethod
    def check_pattern(cmd_str, raw_pattern):
        """
        проверяет регуляркой есть ли в строке cmd {*}

        :param cmd_str: вызываемая командная строка
        :return: bool
        """
        pattern = re.compile(raw_pattern)
        return True if re.search(pattern, cmd_str) else False

    def make_job_param_dict(self, db_field):
        """
        сосдает словарь файлов или именованных агрументов в зависимости от того что передано
        :param db_field: наименование поля в БД
        :return:
        """
        job_dict = dict()
        job_dict_string = self.select_db_column(db_field, 'job_id', self.job_id)[0][db_field]
        if job_dict_string:
            syslog.syslog(syslog.LOG_DEBUG, 'make_jo_{}_dict ... {}'.format(db_field, job_dict_string))
            for obj in job_dict_string.split():
                syslog.syslog(syslog.LOG_DEBUG, 'obj = {}'.format(obj))
                param = obj.split('=')
                job_dict[param[0]] = param[1]
                print('{} - {}'.format(param[0], param[1]))
        return job_dict

    @property
    def get_job_handling_error(self):
        return self.select_db_column('error', 'job_id', self.job_id)[0]['error']

    @property
    def get_job_type(self):
        return self.select_db_column('task_type', 'job_id', self.job_id)[0]['task_type']

    def write_log(self, msg):
        """
        функция записи в сислог + в файл
        :param msg:
        :return:
        """
        self.log_file.write(msg)
        syslog.syslog(syslog.LOG_INFO, msg)

    def param_in_cmd_inject(self, step_cmd):
        """
        Вставляет в строку cmd пути до файлов

        :param step_cmd: строка cmd
        :return: новую строку cmd
        """
        files_pattern = '\(\*.*\*\)'
        kwargs_pattern = '\(~.*~\)'
        new_cmd_string = step_cmd
        if self.check_pattern(step_cmd, files_pattern):
            for obj in self.job['job']['files']['alias']:
                rep_str = '(*{}*)'.format(obj)
                new_cmd_string = new_cmd_string.replace(rep_str, self.job_files[obj])
        if self.check_pattern(step_cmd, kwargs_pattern):
            for obj in self.job['job']['kwargs']['alias']:
                rep_str = '(~{}~)'.format(obj)
                new_cmd_string = new_cmd_string.replace(rep_str, self.job_kwargs[obj])
        return new_cmd_string

    def make_system_reverse(self):
        msg = "пытаемся восстановить систему {0}\n".format(datetime.now())
        self.write_log(msg)
        with open(self.get_settings('job_json_conf_path')) as conf:
            json_conf = json.load(conf)
            recovery_job = json_conf.get(self.job_type, None)
            key = self.job.get('error', None).get('handling', None)
            recovery_dict = OrderedDict(key)
        if recovery_job is None or key is None:
            msg = "Команды восстановления отсутствуют в json файле для {0}\n".format(self.job_type)
            self.write_log(msg)
            return self.log_file_path
            # raise WrongJsonFormatException()
        for step_number, cmd in recovery_dict.iteritems():
            if step_number in self.completed_step:
                if self.job_handler(step_number, recovery_dict):
                    msg = "{} Команда восстановления '{}' завершилась не успешно\n".format(cmd, datetime.now())
                    self.write_log(msg)
                    self.update_db_column('recovery', 1, 'job_id', self.job_id)
                    break
                self.update_db_column('step_number',
                                      step_number,
                                      'job_id',
                                      self.job_id)
                self.completed_step.remove(step_number)
                self.update_db_column('completed_steps',
                                      ' '.join(self.completed_step),
                                      'job_id',
                                      self.job_id)
                msg = "Команда '{}' завершена успешно\n".format(cmd)
                self.write_log(msg)
        else:
            self.update_db_column('recovery', 0, 'job_id', self.job_id)
            msg = "{} Процедуры восстановления завершилась успешно\n".format(datetime.now())
            self.write_log(msg)
        self.update_db_column('status', 0, 'job_id', self.job_id)
        self.update_db_column('date_finish',
                              datetime.now().strftime(self.get_settings('date_format')),
                              'job_id',
                              self.job_id)
        return self.log_file_path


class WrongJsonFormatException(Exception):
    def __init___(self, *args):
        Exception.__init__(self, "Wrong handling json file format in section: {0}".format(*args))
