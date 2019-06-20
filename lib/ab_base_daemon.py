# -*- coding: utf-8 -*-

import os

from python_sz_daemon.base_daemon import BaseDaemon
from ab_dispatcher.socket_listener import ABSocketListener


class ABBaseDaemon(BaseDaemon):

    def __init__(self, pidfile, conf_dict, log_name, *args, **kwargs):
        super(ABBaseDaemon, self).__init__(pidfile, log_name, *args, **kwargs)
        self.conf_dict = conf_dict

    def run(self):
        if os.path.isfile(self.conf_dict('socket_path')):
            os.remove(self.conf_dict('socket_path'))
        with ABSocketListener(self.conf_dict) as socket_listener:
            socket_listener.run()
