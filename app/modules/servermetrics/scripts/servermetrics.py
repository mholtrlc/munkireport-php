#!/usr/bin/env python

"""
Based on script by CCL Forensics
"""

import sys
sys.path.append('/usr/local/munki/munkireportlib')
import os
import os.path as path
import re
import ccl_asldb
import json

# Event Type Strings To array position
EVENTS = {  'filesharing.sessions.afp': 0,
            'filesharing.sessions.smb': 1,
            'caching.bytes.fromcache.toclients': 2,
            'caching.bytes.fromorigin.toclients': 3,
            'caching.bytes.frompeers.toclients': 4,
            'system.cpu.utilization.user': 5,
            'system.memory.physical.wired': 6,
            'system.memory.physical.active': 7,
            'system.cpu.utilization.idle': 8,
            'system.memory.physical.free': 9,
            'system.network.throughput.bytes.in': 10,
            'system.memory.pressure': 11,
            'system.cpu.utilization.system': 12,
            'system.network.throughput.bytes.out': 13,
            'system.cpu.utilization.nice': 14,
            'system.memory.physical.inactive': 15}


def __main__():

    input_dir = '/var/log/servermetricsd/'
    output_file_path = '/usr/local/munki/preflight.d/cache/servermetrics.json'

    out = {}

    for file_path in os.listdir(input_dir):
        file_path = path.join(input_dir, file_path)
        print("Reading: \"{0}\"".format(file_path))
        try:
            f = open(file_path, "rb")
        except IOError as e:
            print("Couldn't open file {0} ({1}). Skipping this file".format(file_path, e))
            continue

        try:
            db = ccl_asldb.AslDb(f)
        except ccl_asldb.AslDbError as e:
            print("Couldn't open file {0} ({1}). Skipping this file".format(file_path, e))
            f.close()
            continue

        timestamp = ''
        
        for record in db:
            #print "%s %s" % (record.timestamp, record.message.decode('UTF-8'))
            fmt_timestamp = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            if fmt_timestamp != timestamp:
                timestamp = fmt_timestamp
                out[timestamp] = [0]*16
            key_val = [x.strip() for x in record.message.split(':')]
            index = EVENTS.get(key_val[0], -1)
            if index >= 0:
                try:
                    out[timestamp][index] = float(key_val[1])
                except ValueError as e:
                    continue

        f.close()

    # Open and write output
    output = open(output_file_path, "w")
    output.write(json.dumps(out))
    output.close()

if __name__ == "__main__":
    __main__()