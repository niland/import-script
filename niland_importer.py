#!/usr/bin/env python
#-*- coding: utf-8 -*-

from pyniland.client import Client
import urllib
import csv
import argparse


class NilandImporter(object):
    def __init__(self, api_key, csv_path):
        self._client = Client(api_key)
        self._tag_collections = dict()
        self._reader = csv.DictReader(open(csv_path, 'rb'), delimiter=';')
        self._headers = self._reader.fieldnames
        self._mandatory_headers = ['title', 'reference']
        for header in self._mandatory_headers:
            if header not in self._headers:
                raise NameError('%s is a mandatory column' % header)

    def process(self):
        normalized_headers = ['reference',
                              'title',
                              'artist',
                              'album',
                              'popularity',
                              'duration',
                              'isrc',
                              'year',
                              'tags',
                              'audio_path',
                              'audio_url']
        for row in self._reader:
            try:
                track = dict()
                for header in self._headers:
                    if header in normalized_headers:
                        if header == 'tags':
                            tag_ids = self._handle_tags(row['tags'])
                            track['tags'] = tag_ids
                        elif 'audio' in header:
                            pass
                        else:
                            track[header] = row[header]
                    else:
                        raise NameError('%s column name is unknown' % header)

                if 'audio_path' in self._headers and 0 != len(row['audio_path']):
                    track['audio'] = open(row['audio_path'], 'rb')
                elif 'audio_url' in self._headers and 0 != len(row['audio_url']):
                    track['audio'] = open(self._download_file(row['audio_url']), 'rb')
                else:
                    raise ValueError('You must provide an audio_path or an audio_url')
                track = self._client.post('tracks', track)
                print 'Reference %s saved Niland ID %s' \
                    % (row['reference'], track['id'])
            except Exception as e:
                print 'Error for "%s": %s' % (row['reference'], e)
                with open("errored.log", 'a') as f:
                    f.write("%s\t%s\n" % (e, row['reference']))

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
    args = parser.parse_args()

    importer = NilandImporter(args.api_key, args.csv_path)
    importer.process()
