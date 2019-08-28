## Brownfield AP Claim
In DNAC when you claim an AP it is based on the WLC being managed and controlled by DNAC.
DNAC has a set of sites the WLC is responsible for, and the AP is able to be claimed to one of them

This script allows a generic WLC config to be pushed to the AP.

### Step 0: change the credential
You need to edit the dnac_config.py file to change the DNAC and user name and password.
If you know how to use environment variables, you can do that instead.

### Step 1: Upload configuration file.
Use the 00_flle_sync.py script to upload the json file for the AP.

This script will look in workfiles/configs directory.  All files are compared with DNAC.  If they are 
present in the DNAC filestore, the SHA1 hash is compared and it will be updated.  If it is not present it will be 
added

```buildoutcfg
./00_file_sync.py 
Skipping File:ap.json (43ed77c0-738b-40c1-b4f5-7ebf86a5d699) SHA1hash:da86e9eb93b0750ca5a94e6aa68e83bb65cf8011


```

A sample configuration file appears below:

```buildoutcfg
$ cat work_files/configs/ap.json 
{
    "apGroup": "default-group",
    "primaryWlcIP": "10.10.10.147",
    "primaryWlcName": "2504-1",
    "apMode": "local"
}

```

### Step 2: Create configuration csv
A CSV file contains a list of serial numbers, product ID and configuraton files

A sample 
```buildoutcfg
$ cat work_files/ap.csv 
name,serial,pid,configfile
ap01,FJC2027F0J0,AIR-AP3802I-B-K9,ap.json
```

### Step 3: Run the script
Use the 10_upload_devices.py file with the configuration file created above.

```buildoutcfg
$ ./10_upload_devices.py work_files/ap2.csv 
Using device file: work_files/ap2.csv
##########################
Device:FJC2027F0J0 name:ap01 workflow:ap.json Status:PLANNED
```

The AP will appear in the UI as planned  waiting for the AP to connect
