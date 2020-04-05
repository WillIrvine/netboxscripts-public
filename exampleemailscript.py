# Example Email Script
# William Irvine 2020

from django.utils.text import slugify

from dcim.constants import *
from dcim.models import Device, DeviceRole, DeviceType, Site
from tenancy.models import Tenant
from circuits.models import Circuit, CircuitType, CircuitTermination
from extras.scripts import *

from django.http import HttpResponse
import csv, urllib.parse
from django.db.models import Q

from django.core.mail import EmailMessage


class ExampleEmailScript(Script):

    class Meta:
        name = "Example Email Script"
        description = "Script that allow the export for data via email for a NB script"
        field_order = ['Client','Email']

    Client = ObjectVar(
        description="Tenant",
        queryset = Tenant.objects.all()
    )
    Email = StringVar(
        description="Email address for export"
    )
	
    def run(self, data):
	
        # Generate a CSV table of new devices
        output = [
            'devicename,deviceid,site,tenant'
        ]
		
		
        for device in Device.objects.filter(tenant__name=data['Client']).filter(Q(status=1) | Q(status=3)):
			
			# Set variables for attributes that may not be present - Logic for unnamed devices and circuit details
			
            devicename = "None"
            site = "None"
            tenant = "None"

            deviceid = str(device.id)
            
            if device.name:
                devicename = device.name
                
            if device.site:
                site = device.site.name
            
            if device.tenant:
                tenant = device.tenant.name
                
			
			
            attrs = [
                devicename,
                deviceid,
                site,
                tenant,
            ]
            output.append(','.join(attrs))
			
            self.log_success("Device {}".format(device))

	     
        email = EmailMessage(
                data['Client'].name+' QRG Export',
                'Please view the attached QRG output from Netbox',
                'test@test.com',
                [data['Email']],
            )
        email.attach(data['Client'].name+'-QRGExport.csv', '\n'.join(output), 'text/csv')
        email.send()	
		
        return '\n'.join(output)
