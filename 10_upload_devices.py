#!/usr/bin/env python
from __future__ import print_function
import csv
import json
import requests
# turn off warninggs
requests.packages.urllib3.disable_warnings()
import os
import os.path
import logging
from dnac_config import DNAC, DNAC_USER, DNAC_PASSWORD
from argparse import ArgumentParser
from dnacentersdk import api



def add_device(dnac, name, serial, pid):
    payload = [{
	"deviceInfo": {
		"hostname": name,
		"serialNumber": serial,
		"pid": pid,
		"sudiRequired": False,
		"userSudiSerialNos": [],
		"stack": False,
		"aaaCredentials": {
			"username": "",
			"password": ""
		}
	}
}]
    #device = post(dnac, "onboarding/pnp-device/import", payload)
    device = dnac.pnp.import_devices_in_bulk(payload=payload)
    #print(json.dumps(device,indent=2))
    # will get back list of success and failures
    try:
        deviceId = device.successList[0].id
    except IndexError as e:
        print ('##SKIPPING device:{},{}:{}'.format(name, serial, device.failureList[0].msg))
        deviceId = None

    return deviceId

def claim_device(dnac,deviceId, workflowId):
    payload = {
	"deviceClaimList": [{
		"deviceId": deviceId,
		"configList": [{
			"configId": "",
			"configParameters": []
		}]
	}],
	"projectId": None,
	"workflowId": workflowId,
	"configId": None,
	"imageId": None,
	"populateInventory": False
}
    #print json.dumps(payload, indent=2)

    #claim = post(dnac,"onboarding/pnp-device/claim", payload)
    claim = dnac.pnp.claim_device(payload=payload)
    #print(json.dumps(claim,indent=2))
    return claim.message

def get_workflow(dnac,workflowName):
    #response = get (dnac, "onboarding/pnp-workflow")
    #print(workflowName)

    workflow = dnac.pnp.get_workflows(name=workflowName)
    if workflow == []:
        raise ValueError("Cannot find template:{}".format(workflowName))
    #print(json.dumps(workflow,indent=2))
    fileid=workflow[0].tasks[0].configInfo.fileServiceId
    return workflow[0].id, fileid

def create_workflow(dnac, workflowName, configid):
    payload = {
    "name": workflowName,
    "description": "",
    "currTaskIdx": 0,
    "tasks": [
        {
            "configInfo": {
                "saveToStartUp": True,
                "connLossRollBack": True,
                "fileServiceId": configid
            },
            "type": "Config",
            "currWorkItemIdx": 0,
            "name": "Config Download",
            "taskSeqNo": 0
        }
    ],
    "addToInventory": False
}
    #print(json.dumps(payload, indent=2))
    response = dnac.pnp.add_a_workflow(payload=payload)
    #print(json.dumps(response))
    return response.id

def get_or_create_workflow(dnac, configfile):
    # look for workflow with the config file or create it
    fileid=None
    files = dnac.file.get_list_of_files(name_space="config")

    for file in files.response:
        if file.name == configfile:
            fileid = file.id

    #print(fileid)
    workflowName = "configfile-{}-AP".format(configfile)
    try:
        workflowid, wkfileid = get_workflow(dnac, workflowName)

    except ValueError:
        workflowid = create_workflow(dnac, workflowName,fileid)

    return workflowid


#def get_template(dnac, configId, supplied_params):
#    params=[]
#    response = get(dnac, "template-programmer/template/{}".format(configId))
#    for vars in response.json()['templateParams']:
#        name = vars['parameterName']
#        params.append({"key": name, "value": supplied_params[name]})
#    #print params
#    return params

def create_and_upload(dnac, devices):

    f = open(devices, 'rt')
    try:
        reader = csv.DictReader(f)
        for device_row in reader:
            #print ("Variables:",device_row)

            try:
                workflowId = get_or_create_workflow(dnac, device_row['configfile'])
            except ValueError as e:
                print("##ERROR {},{}: {}".format(device_row['name'],device_row['serial'], e))
                continue

            #params = get_template(dnac, configId, device_row)

            deviceId = add_device(dnac, device_row['name'], device_row['serial'], device_row['pid'])
            if deviceId is not None:
                #claim
                claim_status = claim_device(dnac, deviceId, workflowId)
                if "Claimed" in claim_status:
                    status = "PLANNED"
                else:
                    status = "FAILED"
                print ('Device:{} name:{} workflow:{} Status:{}'.format(device_row['serial'],
                                                                    device_row['name'],
                                                                    device_row['configfile'],
                                                                    status))
    finally:
        f.close()

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument( 'devices', type=str,
            help='device inventory csv file')
    args = parser.parse_args()
    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    dnac = api.DNACenterAPI(base_url='https://{}:443'.format(DNAC),
                                username=DNAC_USER,password=DNAC_PASSWORD,verify=False,version="1.3.0")
    print ("Using device file:", args.devices)

    print ("##########################")
    create_and_upload(dnac, devices=args.devices)
