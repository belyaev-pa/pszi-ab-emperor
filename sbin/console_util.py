#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import socket
import sys
import json
import uuid
from   ab_dispather.parse_conf import parse_conf


CONF_FILE_PATH = '/etc/ab-dispather/ab-dispather.conf'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start handling job with provided type')
    parser.add_argument('job_type', type=str, help='Job type for handling')
    parser.add_argument('job_args', type=str, help='string with args alias=/path/to/file space separated')
    args = parser.parse_args()
    conf_dict = parse_conf(CONF_FILE_PATH)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_address = conf_dict['socket_path']
    message = json.dumps(dict(
        job_id=str(uuid.uuid4()),
        job_type=args.job_type,
        manager_type='local',
        arguments=args.job_args
    ))
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
    print('log is here: {}'.format(answer_received))
