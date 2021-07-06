#!/usr/bin/env python
from __future__ import print_function
import json
import requests
import sys
# turn off warninggs
requests.packages.urllib3.disable_warnings()

import logging
from dnac_config import DNAC, DNAC_USER, DNAC_PASSWORD
from argparse import ArgumentParser
from dnacentersdk import api

def main(dnac,filename):
    workflowName="configfile-{}-AP".format(filename)
    workflow = dnac.pnp.get_workflows(name=workflowName)
    if workflow == []:
        raise ValueError("Cannot find template:{}".format(workflowName))
    # print(json.dumps(workflow,indent=2))
    print('deleting: {}'.format(workflow[0].id))
    result = dnac.pnp.delete_workflow_by_id(id=workflow[0].id)
    print(json.dumps(result))

if __name__ == "__main__":
    dnac = api.DNACenterAPI(base_url='https://{}:443'.format(DNAC),
                                username=DNAC_USER,password=DNAC_PASSWORD,verify=False,version="1.3.0")
    main(dnac,sys.argv[1])