# -*- coding: utf-8 -*-
import sqlite3
import syslog
import sys
from datetime import datetime


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class BaseDB(object):
    """
    Класс для реализации менеджера контекста для создания и закрытия соединения с БД
    + пару полезных функций
    """
    def __init__(self, conf_dict):
        """
        конструктор класса
        тут подключаемся к базе sqllite и смотрим есть ли табличка с которой мы будем работать
        если нет - создаем
        :param conf_dict:
        """
        self.conf_dict = conf_dict
        syslog.openlog(self.get_settings('log_name'))
        sql_path = self.get_settings('sqlite3_db_path')
        try:
            self.conn = sqlite3.connect(sql_path)
        except sqlite3.Error as err:
            syslog.syslog(syslog.LOG_ERR, 'Не могу выполнить подключение к БД {} ({})'.format(sql_path, err))
            sys.exit('can`t connect to DB...')
        else:
            syslog.syslog(syslog.LOG_INFO, 'Подключение к БД {} прошло успешно...'.format(sql_path))
            self.check_table_or_create()

    def __enter__(self):
        """
        Необходимые "магические методы" для реалзации функционала with
        Использование:
        with RabbitMQSender() as sender_obj:
            # use sender_obj (используем объект тут)
        :return:
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Необходимые "магические методы" для реалзации функционала with
        :param exc_type:
        :param exc_value:
        :param traceback:
        :return:
        """
        # syslog.syslog(syslog.LOG_INFO,
        #               '{} Close database connection...{}'.format(datetime.now(),
        #                                                          traceback.format_exc(limit=2)))
        self.conn.close()

    def update_db_column(self, column, value, condition, parameter):
        """
        Обновление ячейки по условию

        :param column: столбец для обновления
        :param value: новое значение
        :param condition: условие
        :param parameter: значение условия
        :return: void
        """
        self.conn.row_factory = dict_factory
        c = self.conn.cursor()
        c.execute("""
                        UPDATE ab_tasks 
                        SET {} = '{}'
                        WHERE {} = '{}';
                        """.format(column, value, condition, parameter))
        c.close()
        self.conn.commit()

    def select_db_column(self, column, condition, parameter):
        """
        выбор нужного столбца с указанными условиями поиска

        :param column: выбираемый столбец
        :param condition: условие
        :param parameter: значение условия
        :return: список словарей со значениями
        """
        self.conn.row_factory = dict_factory
        c = self.conn.cursor()
        c.execute("""
                        SELECT {}
                        FROM ab_tasks 
                        WHERE {} = '{}';
                        """.format(column, condition, parameter))
        return c.fetchall()

    def select_db_row(self, condition, parameter):
        """
        выбор нужного столбца с текущим айди

        :param condition: условие
        :param parameter: значение условия
        :return: список слвоарей со значениями
        """
        self.conn.row_factory = dict_factory
        c = self.conn.cursor()
        c.execute("""
                        SELECT *
                        FROM ab_tasks 
                        WHERE {} = '{}';
                        """.format(condition, parameter))
        return c.fetchall()

    def insert_into_table(self, insert_tuple):
        """
        вставка новой записи при инициализации новой задачи на основе кортежа сл формата:
        ('job_id', 'status', 'step_number', 'arguments', 'task_type',
        'manager_type', 'completed_steps', 'date_start', 'date_finish',)
        :param insert_tuple:
        :return: void
        """
        c = self.conn.cursor()
        c.execute("""
                        INSERT INTO ab_tasks (                       
                        job_id,
                        status,
                        error,                        
                        step_number,
                        arguments,
                        kwargs,
                        task_type,
                        manager_type,
                        completed_steps,
                        date_start,
                        date_finish)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, insert_tuple)
        c.close()
        self.conn.commit()

    def check_table_or_create(self):
        c = self.conn.cursor()
        c.execute("""            
                        CREATE TABLE IF NOT EXISTS ab_tasks (
                        'id'              INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        'job_id'          VARCHAR                           NOT NULL,
                        'status'          INTEGER                           NOT NULL,
                        'error'           INTEGER                           NOT NULL,                        
                        'step_number'     VARCHAR                           NOT NULL,
                        'arguments'       TEXT                              NOT NULL,
                        'kwargs'          TEXT                              NOT NULL,
                        'task_type'       VARCHAR                           NOT NULL,
                        'manager_type'    VARCHAR                           NOT NULL,                        
                        'completed_steps' VARCHAR,
                        'date_start'      VARCHAR,
                        'date_finish'     VARCHAR,
                        'recovery'        INTEGER,                        
                        UNIQUE ('job_id')
                        );
                        """)
        c.close()
        self.conn.commit()

    def get_settings(self, setting):
        if type(self.conf_dict) is not dict:
            msg = 'conf_dict должен быть словарем.'
            syslog.syslog(syslog.LOG_ERR, msg)
            raise AttributeError(msg)
        try:
            prop = self.conf_dict[setting]
        except KeyError:
            msg = "Не могу найти необходимый параметр параметр {0} в конфигурационном файле".format(setting)
            syslog.syslog(syslog.LOG_ERR, msg)
            raise KeyError(msg)
        return prop


class SettingIsNoneException(Exception):
    pass
