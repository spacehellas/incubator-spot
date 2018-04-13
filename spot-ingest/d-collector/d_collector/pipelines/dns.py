'''
    Methods that will be used to process and prepare dns data, before being sent to
Kafka cluster.
'''

import logging
import re
import sys
import tempfile

from datetime import datetime
from ..utils  import popen

COMMAND = 'tshark -r {0} {1} > {2}'
EPOCH   = datetime(1970, 1, 1)

def convert(pcap, tmpdir, opts='', prefix=None):
    '''
        Convert `pcap` file to a comma-separated output format.

    :param pcap    : Path of binary file.
    :param tmpdir  : Path of local staging area.
    :param opts    : A set of options for `tshark` command.
    :param prefix  : If `prefix` is specified, the file name will begin with that;
                     otherwise, a default `prefix` is used.
    :returns       : Path of CSV-converted file.
    :rtype         : ``str``
    :raises OSError: If an error occurs while executing the `tshark` command.
    '''
    logger = logging.getLogger('SHIELD.DC.PROCESS.DNS')

    with tempfile.NamedTemporaryFile(prefix=prefix, dir=tmpdir, delete=False) as fp:
        command = COMMAND.format(pcap, opts, fp.name)

        popen(command, raises=True)
        return fp.name

def prepare(csvfile, max_req_size):
    '''
        Prepare text-formatted data for transmission through the Kafka cluster.

        This method takes a CSV file and groups it into segments, according to the
    pattern '%Y%m%d%h'. If the size of each segment is greater than the maximum size
    of a request, then divides each segment into smaller ones so that they can be
    transmitted.

    :param csvfile     : Path of CSV-converted file; result of `convert` method.
    :param max_req_size: The maximum size of a request.
    :returns           : A generator which yields the timestamp (in milliseconds) and a
                         list of lines from the CSV-converted file.
    :rtype             : :class:`types.GeneratorType`
    :raises IOError    : If the given file has no any valid line.
    '''
    msg_list  = []
    msg_size  = segmentid = 0
    logger    = logging.getLogger('SHIELD.DC.PROCESS.DNS')
    partition = timestamp = None
    pattern   = re.compile('[0-9]{10}.[0-9]{9}')

    with open(csvfile, 'r') as fp:
        for line in fp:
            value = line.strip()
            if not value: continue

            match = pattern.search(value.split(',')[2])
            if not match: continue

            size  = sys.getsizeof(value)
            # .........................assume the first 15 characters of the line, as
            # the `partition` - and not the result of `search` - e.g. 'Sep  8, 2017 11'
            if value[:15] == partition and (msg_size + size) < max_req_size:
                msg_list.append(value)
                msg_size += size
                continue

            # .........................if the hour is different or the message size is
            # above the maximum, then yield existing list and continue with an empty one
            if timestamp:
                logger.debug('Yield segment-{0}: {1} lines, {2} bytes'.format(segmentid,
                    len(msg_list), msg_size))
                segmentid += 1

                yield (int(timestamp.total_seconds() * 1000), msg_list)

            msg_list  = [value]
            msg_size  = size
            partition = value[:15]
            timestamp = datetime.fromtimestamp(float(match.group())) - EPOCH

    # .................................send the last lines from the file. The check of
    # `timestamp` is in case the file is empty and `timestamp` is still ``None``.
    if not timestamp:
        raise IOError('CSV-converted file has no valid lines.')

    logger.debug('Yield segment-{0}: {1} lines, {2} bytes'.format(segmentid,
        len(msg_list), msg_size))

    yield (int(timestamp.total_seconds() * 1000), msg_list)
