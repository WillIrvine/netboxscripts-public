###########################
#                         #
# Report for Checking     #
# Duplicate Serials       #
# and missing serials     #
#                         #
# - William Irvine - 2021 #
# - V1.0                  #
###########################


from extras.reports import Report
from dcim.models import Device

class netboxInventoryCheck(Report):
    description = "Check that there are no duplicate or missing serial numbers in Netbox"

    def test_Netbox_InventoryDevices(self):
        
		# Get all devices and add to deviceList object
        deviceList = Device.objects.all()
        
		# set lists for all serials and duplicate entires
		serialList = []
        dupList = []
        
		# For all devices if the serial isn't empty add to the serial list, this will be used for comparison, flag warning if there is no serial.
        for device in deviceList:
            if device.serial != "":
                serialList.append(device.serial)
            else:
                self.log_warning(device,"Device Missing Serial Number")
        

		# For all devices, if the serial is in the list more than once (itself), add to the diplicate list, else flag success
        for device in deviceList:
         
            if (serialList.count(device.serial)) > 1:
                dupList.append(device.serial)
            else: 
                self.log_success("No Issues")

		# Sort the duplicate list and remove the double entries ready for the report result
        sorted_dupList = sorted(dupList)
        sorted_dupList_singular = list(dict.fromkeys(sorted_dupList))
        
		# Flag failure for all serials in the duplicate list
        for serial in sorted_dupList_singular:
            self.log_failure(serial,"Duplicate Serial")
