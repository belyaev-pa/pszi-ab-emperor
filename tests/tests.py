# -*- coding: utf-8 -*-
import os
import sys
import datetime
import errno
from collections import namedtuple
from base_db import BaseDB



"""
Код был использован для ручного тестирвоания функционала
"""
LOG_NAME = 'ab_log'
SQLLITE_PATH = 'ab.sqlite3'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
JOB_HANDLER_PID_FILE_PATH = '/var/run/ab_demon.pid'
conf_dict = dict(
    log_name=LOG_NAME,
    sqlite3_db_path=SQLLITE_PATH,
    JOB_JSON_CONF_PATH='../share/handle_scheme.json',
    DATE_FORMAT=DATE_FORMAT,
    LOG_FILES_DIR='../test/',
    )

class TestClass(BaseDB):
    def __init__(self, conf_d):
        super(TestClass, self).__init__(conf_d)
        self.job_id = 'fc0390a2-eff3-4d05-a8ff-f3c17beb7424'
        DBRow = namedtuple('DBRow', [
            'job_id',
            'status',
            'error',
            'step_number',
            'arguments',
            'kwargs',
            'task_type',
            'manager_type',
            'completed_steps',
            'date_start',
            'date_finish'
        ])
        db_row = DBRow(job_id=self.job_id,
                       status='1',
                       error='0',
                       step_number='step_1',
                       arguments=str('Привет мир'),
                       kwargs=str('Oración de la mañana'),
                       task_type='123445апв',
                       manager_type='dfgdfgvcbвапOración de la mañana',
                       completed_steps='',
                       date_start='',
                       date_finish='', )
        self.insert_into_table(db_row)

    def test(self):
        self.update_db_column('step_number',
                              'Пиздец',
                              'arguments',
                              'Привет мир')
        print(self.select_db_column('task_type', 'job_id', self.job_id)[0]['task_type'])
        print(self.select_db_row('kwargs', 'Oración de la mañana'))

if __name__ == '__main__':
    t = TestClass(conf_dict)
    t.test()

