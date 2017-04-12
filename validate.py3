#!/usr/local/bin/python3

import requests
import sys
import re
import os
from lxml import etree
from multiprocessing import Pool, Lock

schema_cache_dir = os.path.expanduser('~/.xmlschemas1')

schemas_lock = Lock()

# Cached schemas.
schemas = {}

url_re = re.compile(r'xsi:schemaLocation="\S+\s+(.+?)"')

def extract_schema_url(path):
    with open(path, encoding='utf-8') as f:
        for line in f:
            match = re.search(url_re, line)
            if match:
                return match.group(1)
    return None

def download_schema(url):
    os.makedirs(schema_cache_dir, exist_ok=True)
    encoded_file_name = url.replace('/', '%2F')
    file_path = os.path.join(schema_cache_dir, encoded_file_name)

    if os.path.isfile(file_path):
        schema_doc = etree.parse(file_path)
    else:
        # DEBUG
        print("Downloading now {}...".format(url))

        response = requests.get(url)
        content = response.content

        # Save into a file.
        with open(file_path, 'wb') as f:
            f.write(content)

        # TODO Should save on reloading from file, and load from memory.
        schema_doc = etree.parse(file_path)

    return etree.XMLSchema(schema_doc)
        
def get_schema(url):
    schema = schemas.get(url)
    if schema:
        return schema
    else:
        schemas_lock.acquire()
        try:
            schema = schemas.get(url)
            if schema:
                return schema
            else:
                schema = download_schema(url)
                schemas[url] = schema
                return schema
        finally:
            schemas_lock.release()

def validate(path):
    url = extract_schema_url(path)
    if url is None:
        # Skip validation if no Schema found.
        print('{}: no schema URL found'.format(path))
        return

    schema = get_schema(url)

    # Create a new XML Schema validating parser rather than caching it.
    parser = etree.XMLParser(schema = schema)

    try:
        etree.parse(path, parser)
        print('{} validates'.format(path), file=sys.stderr)
    except Exception as e:
        print('{}: {}'.format(path, e), file=sys.stderr)
        print('{} fails to validate'.format(path), file=sys.stderr)

def validate_all_cmdi(root_dir):
    with Pool() as p:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.cmdi'):
                    p.apply_async(validate, (os.path.join(root, file),))
        p.close()
        p.join()

# The main program.
if __name__ == '__main__':
    # TODO Better option handling
    root_dir = sys.argv[1]

    validate_all_cmdi(root_dir)
