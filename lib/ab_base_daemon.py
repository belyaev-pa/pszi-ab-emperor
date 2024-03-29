# -*- coding: utf-8 -*-

import os

from python_sz_daemon.base_daemon import BaseDaemon
from ab_dispatcher.socket_listener import ABSocketListener


class ABBaseDaemon(BaseDaemon):

    def __init__(self, pidfile, conf_dict, log_name, *args, **kwargs):
        super(ABBaseDaemon, self).__init__(pidfile, log_name, *args, **kwargs)
        self.conf_dict = conf_dict
        socket_path = self.conf_dict.get('socket_path' , None)
        if socket_path is None:
            exit('Путь до сокет файла не указан в конфигурационном файле')
        if os.path.exists(socket_path):
            os.remove(socket_path)

    def run(self):
        with ABSocketListener(self.conf_dict) as socket_listener:
            socket_listener.run()
