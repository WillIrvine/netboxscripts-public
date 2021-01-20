###########################
#                         #
# Report for Checking     #
# Duplicate Serials       #
# and missing serials     #
#                         #
# - William Irvine - 2021 #
# - V1.0                  #
###########################



from tenancy.models import Tenant
from extras.reports import Report
from dcim.models import Device, DeviceRole, DeviceType, Site
from dcim.choices import DeviceStatusChoices, SiteStatusChoices

from django.db.models import Q

import requests
import json
import os
import re
import yaml
import time

class netboxInventoryCheck(Report):
    description = "Check that there are no duplicate or missing serial numbers in Netbox"

    def test_Netbox_InventoryDevices(self):
        
        deviceList = Device.objects.all()
        serialList = []
        dupList = []
        
        for device in deviceList:
            if device.serial != "":
                serialList.append(device.serial)
            else:
                self.log_warning(device,"Device Missing Serial Number")
            
        for device in deviceList:
         
            if (serialList.count(device.serial)) > 1:
                dupList.append(device.serial)
            else: 
                self.log_success("No Issues")

        sorted_dupList = sorted(dupList)
        sorted_dupList_singular = list(dict.fromkeys(sorted_dupList))
        
        for serial in sorted_dupList_singular:
            self.log_failure(serial,"Duplicate Serial")
