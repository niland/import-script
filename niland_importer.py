#!/usr/bin/env python
#-*- coding: utf-8 -*-

from nilandapi.client import Client
import urllib
import csv
import argparse

class NilandImporter(object):
    def __init__(self, api_key, csv_path):
        self._client = Client(api_key)
        self._reader = csv.reader(open(csv_path, 'rb'), delimiter=';')

    def process(self):
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

        for row in self._reader:
            try:
                if len(headers) != len(row):
                    raise Exception('Malformed row. Expected %s field, having %s.' % (len(headers), len(row)))
                tag_ids = self._handle_tags(row[headers['tags']])
                track = {
                    'reference': row[headers['reference']],
                    'title': row[headers['title']],
                    'artist': row[headers['artist_name']],
                    'album': row[headers['album_name']],
                    'popularity': row[headers['popularity']],
                    'duration': row[headers['duration']],
                    'isrc': row[headers['isrc']],
                    'year': row[headers['year']],
                    'tags': tag_ids
                }
                if 0 != len(row[headers['audio_path']]):
                    track['audio'] = open(row[headers['audio_path']], 'rb')
                if 0 != len(row[headers['audio_url']]):
                    track['audio'] = open(self._download_file(row[headers['audio_url']]), 'rb')
                track = self._client.post('tracks', track)
                print 'Line %s saved Niland ID %s' % (self._reader.line_num, track['id'])
            except Exception as e:
                print 'Line %s error "%s"' % (self._reader.line_num, e)

    def _handle_tags(self, value):
        tag_ids = []
        if len(value) > 0:
            tags = value.split(',')
            for element in tags:
                data = element.split('|')
                if 2 != len(data):
                    raise Exception('Malformed tag: "%s"' % element)
                tc_name = data[0]
                tag_title = data[1]
                tc = self._create_tag_collection(tc_name)
                tag = self._create_tag(tc_name, tag_title)
                tag_ids.append(tag['id'])
        return tag_ids

    def _create_tag_collection(self, name):
        existing = self._client.get('tag-collections', {'query': name, 'page_size': 1})
        if 1 == len(existing['data']):
            return existing['data'][0]
        return self._client.post('tag-collections', {'name': name})

    def _create_tag(self, tc_name, title):
        response = self._client.get('tags', {'query': title})
        for tag in response['data']:
            if tc_name == tag['tag_collection']['name']:
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
    args = parser.parse_args()

    importer = NilandImporter(args.api_key, args.csv_path)
    importer.process()
