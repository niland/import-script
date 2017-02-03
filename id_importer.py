#!/usr/bin/env python
# coding: utf-8

from pyniland.client import Client
import urllib
import csv
import argparse
from subprocess import call
import os
from joblib import Parallel, delayed


def process_one(row):
    try:
        track = {
            'title': row,
            'reference': row
        }

        track = importer._client.post('tracks', track)
        print('Reference %s saved Niland ID %s' %
              (row['reference'], track['id']))
    except Exception as e:
        if str(e) == "None":
            if "http_code" in dir(e):
                e = e.http_code
        print 'Error for "%s": %s' % (row['reference'], e)
        with open("errored.log", 'a') as f:
            f.write("%s\t%s\n" % (e, row['reference']))


class NilandImporter(object):
    def __init__(self, api_key, csv_path, start_line=0):
        self._client = Client(api_key)
        self._reader = csv.reader(open(csv_path, 'rb'))
        if start_line:
            for k in range(start_line):
                next(self._reader)
        self._mandatory_headers = ['title', 'reference']

    def process(self, njobs):
        Parallel(n_jobs=njobs, verbose=11)(
            delayed(process_one)(row) for row in self._reader
        )

    def process_errored(self, njobs):
        with open("errored.log", 'r') as f:
            rows = f.read().split('\n')
        open('errored.log', 'w').close()
        references_to_process = [row.split('\t')[-1] for row in rows]
        references_to_process = set(references_to_process)
        rows_to_process = []
        for k, row in enumerate(self._reader):
            for reference in references_to_process:
                if row['reference'] == reference:
                    rows_to_process += [row]
        Parallel(n_jobs=njobs, verbose=11)(
            delayed(process_one)(row) for row in rows_to_process
        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Niland Catalog Importer')
    parser.add_argument('--api-key', help='Your API key', required=True)
    parser.add_argument(
        '--csv-path', help='Full path to the csv file', required=True
    )
    parser.add_argument(
        '--njobs', help='Number of parallel jobs to throw',
        required=False, default=1
    )
    parser.add_argument(
        '--start-line', help='Line from which to start uploading',
        required=False, type=int
    )
    parser.add_argument(
        '--errored', help='Process only references listed in errored.log'
        '(This will erase the content of errored.log)',
        required=False, action="store_true"
    )
    args = parser.parse_args()

    global importer
    importer = NilandImporter(
        args.api_key, args.csv_path, args.start_line
    )
    if args.errored:
        importer.process_errored(int(args.njobs))
    else:
        importer.process(int(args.njobs))
