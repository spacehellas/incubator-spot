#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Main command-line entry point.
'''

import json
import os
import pipelines
import sys

from argparse import ArgumentParser, HelpFormatter
from utils    import authenticate, get_logger

__version__ = '0.7.3 beta'

STATE = {
    'database_name': None,
    'kerberos': {},
    'streaming': {},
    'zkQuorum': None
}

def main():
    try:
        args  = parse_args()
        conf  = json.loads(args.config_file.read())

        # .............................set up logger
        get_logger('SHIELD.WORKER', args.log_level)

        # .............................set up STATE
        for key in conf.keys():
            if isinstance(conf[key], basestring) and conf[key].strip() == '':
                continue

            if key in STATE.keys():
                STATE[key] = conf[key]

        # .............................check kerberos authentication
        if os.getenv('KRB_AUTH'):
            authenticate(**STATE['kerberos'])

        # .............................instantiate Streaming Worker
        for key in STATE['streaming'].keys():
            if (isinstance(STATE['streaming'][key], basestring) and
                STATE['streaming'][key].strip() == ''):
                del STATE['streaming'][key]

        streaming_worker(args.flow, args.topic, args.partition, STATE['database_name'],
            **STATE['streaming'])

    except SystemExit: raise
    except:
        sys.excepthook(*sys.exc_info())
        sys.exit(1)

def parse_args():
    '''
        Parse command-line options found in 'args' (default: sys.argv[1:]).

    :returns: On success, a namedtuple of Values instances.
    '''
    parser   = ArgumentParser(
        prog='worker',
        description='Worker daemon consumes incoming messages from the Kafka cluster and '
            'stores them in the big data infrastructure.',
        epilog='END',
        formatter_class=lambda prog: HelpFormatter(prog, max_help_position=36, width=80),
        usage='worker [OPTIONS]... ')

    # .................................set optional arguments
    parser._optionals.title = 'Optional Arguments'

    parser.add_argument('-c', '--config-file', metavar='FILE', type=file,
        default=os.path.expanduser('~/.worker.json'),
        help='path of configuration file')

    parser.add_argument('-l', '--log-level', metavar='STRING', default='INFO',
        help='determine the level of the logger')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'
        .format(__version__))

    # .................................set required arguments
    required = parser.add_argument_group('Required Arguments')

    required.add_argument('-p', '--partition', required=True, metavar='INTEGER',
        help='number of partition to consume')

    required.add_argument('--topic', required=True, metavar='STRING',
        help='name of topic where the messages are published')

    required.add_argument('-t', '--type', choices=pipelines.__all__, required=True,
        help='type of data that will be ingested', metavar='STRING')

    return parser.parse_args()

def streaming_worker(datatype, topic, partition, db_name, **kwargs):
    '''
        Start Streaming Worker using `spark2-submit` command.

    :param datatype : Type of data that will be ingested
    :param topic    : Topic where the messages are published.
    :param partition: Number of partition to consume.
    :param db_name  : Name of the database in Hive.
    '''
    command = 'spark2-submit'

if __name__ == '__main__': main()
