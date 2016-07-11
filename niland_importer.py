#!/usr/bin/env python
#-*- coding: utf-8 -*-

from nilandapi.client import Client
import urllib
import csv
import argparse
from joblib import Parallel, delayed

headers = {
    'reference': 0,
    'title': 1,
    'artist_name': 2,
    'album_name': 3,
    'popularity': 4,
    'duration': 5,
    'isrc': 6,
    'year': 7,
    'tags': 8,
    'audio_path': 9,
    'audio_url': 10
}


def process_one(row):
    try:
        if len(headers) != len(row):
            raise Exception('Malformed row. Expected %s field, having %s.' % (len(headers), len(row)))
        tag_ids = importer._handle_tags(row['tags'])
        try:
            track = {
                'reference': row['reference'],
                'title': row['title'].title(),
                'artist': row['artist_name'],
                'album': row['album_name'],
                'popularity': row['popularity'],
                'duration': row['duration'],
                'isrc': row['isrc'],
                'year': row['year'],
                'tags': tag_ids
            }
            requ = 'tracks/reference/%s' % row['reference']
            print requ
            existing_track = importer._client.get(requ)
            print 'Reference %s already saved.' % (row['reference'])
            change, track = preprocess_patch(existing_track, track)
            if change:
                print "Patching"
                track = importer._client.patch('tracks/%d' % existing_track['id'], track)
            else:
                print "Passing"
        except KeyboardInterrupt:
            raise KeyboardInterrupt()
        except:
            if 0 != len(row['audio_path']):
                track['audio'] = open(row['audio_path'], 'rb')
            if 0 != len(row['audio_url']):
                track['audio'] = open(importer._download_file(row['audio_url']), 'rb')
            track = importer._client.post('tracks', track)
            print 'Reference %s saved Niland ID %s' % (row['reference'], track['id'])
    except Exception as e:
        print 'Error for "%s": %s' % (row['reference'], e)
        with open("errored.log", 'a') as f:
            f.write("%s\t%s\n" % (e, row['reference']))


def preprocess_patch(existing_track, new_track):
    track_to_patch = dict()
    change = False
    for header in new_track.keys():
        if header == "tags":
            track_to_patch[header] = list(set(new_track['tags'] + [tag['id'] for tag in existing_track[header]]))
            for el in track_to_patch[header]:
                if el not in [tag['id'] for tag in existing_track[header]]:
                    change = True
        elif header == "artist":
            if new_track["artist"]:
                if not existing_track["artist"] or "name" not in existing_track["artist"] or existing_track["artist"]["name"] != new_track["artist"]:
                    track_to_patch["artist"] = new_track["artist"]
                    change = True
            elif existing_track["artist"] and "name" in existing_track["artist"] and existing_track["artist"]["name"] == new_track["artist"]:
                track_to_patch["artist"] = existing_track["artist"]["name"]
            else:
                track_to_patch["artist"] = ""
        elif header == "album":
            if new_track["album"]:
                if not existing_track["album"] or "name" not in existing_track["album"] or existing_track["album"]["name"] != new_track["album"]:
                    track_to_patch["album"] = new_track["album"]
                    change = True
            elif existing_track["album"] and "name" in existing_track["album"] and existing_track["album"]["name"] == new_track["album"]:
                track_to_patch["album"] = existing_track["album"]["name"]
            else:
                track_to_patch["album"] = ""
        else:
            if not new_track[header] or str(existing_track[header]) == new_track[header]:
                track_to_patch[header] = existing_track[header]
            else:
                track_to_patch[header] = new_track[header]
                change = True
    return change, track_to_patch


class NilandImporter(object):
    def __init__(self, api_key, csv_path, start_line=0):
        self._client = Client(api_key)
        if not start_line:
            self._reader = csv.DictReader(open(csv_path, 'rb'), delimiter=';')
            _ = self._reader.fieldnames
        else:
            self._reader = csv.DictReader(open(csv_path, 'rb'), delimiter=';')
            for k in range(start_line):
                next(self._reader)
        self._tag_collections = dict()

    def process(self, njobs):
        Parallel(n_jobs=njobs, verbose=11)(delayed(process_one)(row) for row in self._reader)

    def process_errored(self, njobs):
        with open("errored.log", 'r') as f:
            rows = f.read().split('\n')
        open('errored.log', 'w').close()
        references_to_process = [row.split('\t')[-1] for row in rows]
        references_to_process = set(references_to_process)
        rows_to_process = []
        for k, row in enumerate(self._reader):
            # print row['reference']
            for reference in references_to_process:
                if row['reference'] == reference:
                    rows_to_process += [row]
        Parallel(n_jobs=njobs, verbose=11)(delayed(process_one)(row) for row in rows_to_process)

    def process_new_tracks(self, njobs):
        page = 1
        page_count = 1
        all_existing_tracks = []
        while page <= page_count:
            print page
            response = self._client.get('tracks', {'page': page, 'page_size': 1000})
            all_existing_tracks += response['data']
            page = response['page'] + 1
            page_count = response['page_count']
        all_existing_references = [track['reference'] for track in all_existing_tracks]
        rows_to_process = []
        for k, row in enumerate(self._reader):
            process_this_one = True
            for reference in all_existing_references:
                if row['reference'] == reference:
                    process_this_one = False
            if process_this_one:
                rows_to_process += [row]
        Parallel(n_jobs=njobs, verbose=11)(delayed(process_one)(row) for row in rows_to_process)


    def _handle_tags(self, value):
        tag_ids = []
        if len(value) > 0:
            tags = value.split(',')
            for element in tags:
                data = element.split('|')
                if 2 != len(data):
                    raise ValueError('Malformed tag: "%s"' % element)
                tc_name = data[0]
                tag_title = data[1]
                if tc_name not in self._tag_collections.keys():
                    tc = self._create_tag_collection(tc_name)
                    if tc:
                        self._tag_collections[tc_name] = dict(tc_id=tc['id'],
                                                              tags=dict())
                if tc_name in self._tag_collections.keys():
                    if tag_title not in self._tag_collections[tc_name]['tags'].keys():
                        try:
                            tag = self._create_tag(tc_name, tag_title)
                        except Exception as e:
                            print e, tc_name, tag_title
                        self._tag_collections[tc_name]['tags'][tag_title] = tag['id']
                    else:
                        tag = dict(id=self._tag_collections[tc_name]['tags'][tag_title])
                    tag_ids.append(tag['id'])
        return tag_ids

    def _create_tag_collection(self, name):
        existing = self._client.get('tag-collections', {'query': name, 'page_size': 1})
        if 1 == len(existing['data']):
            return existing['data'][0]
        return self._client.post('tag-collections', {'name': name})

    def _create_tag(self, tc_name, title):
        page = 1
        page_count = 1
        data = []
        while page <= page_count:
            response = self._client.get('tags', {'query': title, 'page': page})
            data += response['data']
            page = response['page'] + 1
            page_count = response['page_count']
        for tag in data:
            if tc_name == tag['tag_collection']['name'] and title == tag['title']:
                return tag
        return self._client.post('tags', {'title': title, 'tag_collection': tc_name})

    def _download_file(self, url):
        audio_file = urllib.URLopener()
        audio_file.retrieve(url, 'temp_audio_file')
        return 'temp_audio_file'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Niland Catalog Importer')
    parser.add_argument('--api-key', help='Your API key', required=True)
    parser.add_argument('--csv-path', help='Full path to the csv file', required=True)
    parser.add_argument('--njobs', help='Number of parallel jobs to throw', required=False, default=1)
    parser.add_argument('--start-line', help='Line from which to start uploading', required=False, type=int)
    parser.add_argument('--errored', help='Process only references listed in errored.log (This will erase the content of errored.log)', required=False, action="store_true")
    parser.add_argument('--new-tracks', help='Process only new-tracks (no PATCHs only POSTs)', required=False, action="store_true")
    args = parser.parse_args()

    global importer
    importer = NilandImporter(args.api_key, args.csv_path, args.start_line)
    if args.errored:
        importer.process_errored(int(args.njobs))
    elif args.new_tracks:
        importer.process_new_tracks(int(args.njobs))
    else:
        importer.process(int(args.njobs))
