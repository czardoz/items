#!/usr/bin/env python
#
# Items - Mongo Project
#
# Copyright (C) 2015 Aniket Panse <aniketpanse@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gevent
import gevent.monkey

gevent.monkey.patch_all()
import os
import sys

# Quick hack because this is not a proper setuptools package
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import logging
import argparse

from gevent.pywsgi import WSGIServer
from items import app


def setup_logging(args):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
    console_handler.setFormatter(formatter)
    if args.verbose:
        console_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)


if __name__ == '__main__':

    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='More detailed logging.')
    args = parser.parse_args()
    setup_logging(args)

    http_server = WSGIServer(('', 8080), app)
    srv_greenlet = gevent.spawn(http_server.serve_forever)

    try:
        gevent.joinall([srv_greenlet])
    except KeyboardInterrupt:
        logging.info('Quitting')