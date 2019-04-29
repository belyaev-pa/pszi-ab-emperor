# -*- coding: utf-8 -*-
# TODO: make right path after test
from lib.base_daemon import Daemon
from socket_listener import ABSocketListener


class ABBaseDaemon(Daemon):

    def run(self):
        with ABSocketListener(self.conf_dict) as socket_listener:
            socket_listener.run()




