###########################
#                         #
# Report for Checking     #
# Devices match their     #
# Device Template         #
# (Interfaces only)       #
#                         #
# - William Irvine - 2021 #
# - V1.0                  #
###########################


# Please note - this requires the 'devicetype-sync' tag
# to be applied to the device template, this helps with 
# slowly progressing through getting devices in sync

from extras.reports import Report
from dcim.models import Device, DeviceType, Interface, InterfaceTemplate

class devicetemplateCheck(Report):
    description = "Check devices with devicetype-sync tag match their template"

    def test_DeviceTemplates(self):
        
        # List of templates with the sync tag applied
        for deviceTemplate in DeviceType.objects.filter(tags__slug="devicetype-sync"):

            int_template_list = []

            # Add Interfaces in template to int_template_list
            for interface in InterfaceTemplate.objects.filter(device_type=deviceTemplate):
                int_template_list.append([interface.name,interface.type])

            # Set Query to match devices that are retured
            for device in Device.objects.filter(device_type=deviceTemplate):

                issues = 0
                int_device_list = []

                # Add Interfaces on device to int_device_list
                for interface in Interface.objects.filter(device=device):
                    int_device_list.append([interface.name,interface.type])

                matchedInt = []

                # Match interfaces and check type is in compliance
                for template_interface in int_template_list:
                    for device_interface in int_device_list:
                        if device_interface[0] == template_interface[0]:
                            # device names match, try match type
                            if device_interface[1] == template_interface[1]:
                                matchedInt.append(template_interface[0])
                            else:
                                self.log_warning(device,"Interface : " +device_interface[0]+ " is type " +device_interface[1]+ " where the template is "+ template_interface[1])
                                issues = issues + 1
                                matchedInt.append(template_interface[0])    

                matchedInt = set(matchedInt)

                template_list_name = []
                for i in int_template_list:
                    template_list_name.append(i[0])

                template_list_name = set(template_list_name)

                int_device_list_name = []
                for i in int_device_list:
                    int_device_list_name.append(i[0])

                int_device_list_name = set(int_device_list_name)

                notOnDevice = template_list_name - matchedInt
                notOnTemplate = int_device_list_name - matchedInt

                for int in notOnDevice:
                    self.log_failure(device,"Interface : " + int + " not on the device but part of template")
                    issues = issues + 1

                for int in notOnTemplate:
                    self.log_failure(device,"Interface : " + int + " not on the template but on device")
                    issues = issues + 1

                if (issues == 0):
                    self.log_success(device)
