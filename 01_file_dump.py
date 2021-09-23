#!/usr/bin/env python
from __future__ import print_function
import json
from dnac_config import DNAC, DNAC_USER, DNAC_PASSWORD
from argparse import ArgumentParser
from dnacentersdk import api
import logging
from file_cache import FileCache
from random import randrange

logger = logging.getLogger(__name__)
def get_files(dnac, namespace):
        files = get(dnac, "dna/intent/api/v1/file/namespace/{nameSpace}".format(nameSpace=namespace))

        for file in files.json()['response']:
            print("{}:{}:{}".format(file['name'], file['fileSize'],file['fileFormat']))


def dump_files(file_cache):
    for file in file_cache._cache.values():
        print("{}:{}:{}".format(file['name'], file['fileSize'], file['fileFormat']))
    total = len(file_cache._cache)
    print("Total:{}".format(total))

    rind = randrange(total+1)
    rand_key = list(file_cache._cache.keys())[rind]
    file = file_cache.lookup(rand_key)
    print("Random key:{}, {}".format(rand_key, file))
def main():
    if True:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.debug("logging enabled")
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    dnac = api.DNACenterAPI(base_url='https://{}:443'.format(DNAC),
                            username=DNAC_USER, password=DNAC_PASSWORD, verify=False, version="1.3.0")
    file_cache = FileCache(dnac, logger)
    dump_files(file_cache)

if __name__ == "__main__":
    main()
