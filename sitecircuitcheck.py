###########################
#                         #
# Report for Checking     #
# Netbox sites are        #
# Accurate                #
#                         #
# - William Irvine - 2020 #
# - V1.0                  #
###########################

# This check runs through and makes sure the status of devices, sites and circuits dont condradict eachother
# This checks
#      - If Retired sites have active circuits or devices
#      - If Active sites have only retired circuits or devices.

from tenancy.models import Tenant
from circuits.choices import CircuitStatusChoices
from circuits.models import Circuit, CircuitType
from extras.reports import Report
from dcim.models import Device, DeviceRole, DeviceType, Site
from dcim.choices import DeviceStatusChoices, SiteStatusChoices

from django.db.models import Q
from jinja2 import Environment, FileSystemLoader
from django.core.mail import EmailMessage

import requests
import json
import os
import re
import yaml
import time


class netboxSiteCheck(Report):
    description = "Check Retired sites dont have active circuits, and there are no active sites with all retired circuits / devices"

    def test_Netbox_sites(self):
        
        
        # Set Query to match sites that are retured
        for site in Site.objects.filter(status=SiteStatusChoices.STATUS_RETIRED):
            
            if Circuit.objects.filter(terminations__site=site).filter(status=CircuitStatusChoices.STATUS_ACTIVE).count() > 0:
                
                message = "Retired site has active circuits"
                self.log_failure(site,message)
                
            if Device.objects.filter(site=site).filter(status=DeviceStatusChoices.STATUS_ACTIVE).count() > 0:

                message = "Retired site has active devices"
                self.log_failure(site,message)
            
        
        # Set Query to match sites that are active
        for site in Site.objects.filter(status=SiteStatusChoices.STATUS_ACTIVE):            
            
            # Get the total number of offline devices at this site.
            decommedDevice = Device.objects.filter(site=site).filter(status=DeviceStatusChoices.STATUS_OFFLINE).count()
           
            # Get the total number of devices at this site.
            totalDevice = Device.objects.filter(site=site).count()
           
            # Check if the amount of Decommed devices equals the number of total devices at this site, zero values are delt with further down i.e 0=0
            if ((decommedDevice == totalDevice)):
                noActiveDevice = True
            else:
                noActiveDevice = False
            
            # Get the count of decomissioned circuits at this site. 
            decommedCircuit = Circuit.objects.filter(terminations__site=site).filter(status=CircuitStatusChoices.STATUS_DECOMMISSIONED).count()
            
            # Get the total count of circuits at this site.
            totalCircuit = Circuit.objects.filter(terminations__site=site).count()
            
            # Check if the amount of Decommed circuits equals the number of total circuits at this site, zero values are delt with further down i.e 0=0
            if ((decommedCircuit == totalCircuit)):
                noActiveCircuit = True
            else:
                noActiveCircuit = False
             
            # Check if there are both only decomissioned devices and circuits at a site, log warning if true
            if ((noActiveDevice == True and totalDevice > 0) and (noActiveCircuit == True and totalCircuit > 0)):
                message = "Active site only has decomissioned devices and circuits"
                self.log_warning(site,message)
                
            # Check if there are only Decomissioned Devices at a site, include sites with no circuits. log warning if true
            elif (((noActiveDevice == True) and totalDevice > 0) and (totalCircuit == 0)):
                message = "Active site only has decomissioned devices"
                self.log_warning(site,message)                
            
            # Check if there are only Decomissioned Circuits at a site, include sites with no deivces. log warning if true
            elif (((noActiveCircuit == True) and totalCircuit > 0) and (totalDevice == 0)):
                message = "Active site only has decomissioned circuits"
                self.log_warning(site,message)    
                
            # Any other scenario is valid, log success for result.    
            else:
                self.log_success("No Issues")
                
