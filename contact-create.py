##############################
#                            #
# Script for building        #
# contacts and making        #
# accociations with objects  #
# William Irvine - 2023      #
#                            #
##############################

## TODO add logic for adding a contact that already exists in the group

from dcim.models import Site
from tenancy.models import Tenant, Contact, ContactGroup, ContactAssignment, ContactRole
from extras.scripts import *
from django.utils.text import slugify

class ContactCreateTenant(Script):

    class Meta:
        name = 'Contact Creation - Tenant'
        description = "Create a new contact and add to Tenant"

    tenant = ObjectVar(
        model=Tenant,
    )

    contact_name = StringVar(
        description="Name of the new Contact"
    )

    contact_number = StringVar(
        description="Phone number of the new Contact",
    )

    contact_email = StringVar(
        description="Email of the new Contact"
        #regex="""/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/"""
    )

    def run(self, data, commit):

        # Find tenant contact group if exists, create if it doesn't
        contact_group_obj_filter=ContactGroup.objects.filter(name=data['tenant'].name)

        if contact_group_obj_filter:
            contact_group_obj = contact_group_obj_filter[0]
            self.log_info("Found Client Contact Group: {}".format(data['tenant'].name))
        else:
            contact_group_obj = ContactGroup(
                name=data['tenant'].name,
                slug=slugify(data['tenant'].name)
            )
            self.log_success("Created Client Contact Group: {}".format(data['tenant']))
            contact_group_obj.save()


        # Find contact if it exists, create if it doesn't
        contact_obj_filter = Contact.objects.filter(name=data['contact_name'],group=contact_group_obj)

        if contact_obj_filter:
            contact_obj = contact_obj_filter[0]
            self.log_warning("Contact: {} already exists, skipping".format(data['contact_name']))
        else:
            # Add new contact
            contact_obj = Contact(
                name=data['contact_name'],
                email=data['contact_email'],
                phone=data['contact_number'],
                group=contact_group_obj,
            )

            contact_obj.save()
            self.log_success("Created Contact: {}".format(data['contact_name']))

        # Find contact assignment if it exists, create if it doesn't
        contact_assignment_obj_filter = ContactAssignment.objects.filter(contact=contact_obj, object_id=data['tenant'].id, content_type=58) # Content_type 58 is the tenant model

        if contact_assignment_obj_filter:
            contact_assignment = contact_assignment_obj_filter[0]
            self.log_warning("Contact Assignment: {} -> {} already exists, skipping".format(contact_obj.name,data['tenant'].name))
        else:

            contact_assignment = ContactAssignment(
                contact=contact_obj,
                object=data['tenant'],
                role=ContactRole.objects.get(pk=1) # Client Contact Role
            )

            contact_assignment.save()
            self.log_success("Created Contact Association: {} -> {}".format(data['contact_name'],data['tenant'].name))

        return "Finished"
    

class ContactCreateSite(Script):

    class Meta:
        name = 'Contact Creation - Site'
        description = "Create a new contact and add to site"

    site = ObjectVar(
        model=Site,
    )

    contact_name = StringVar(
        description="Name of the new Contact"
    )

    contact_number = StringVar(
        description="Phone number of the new Contact"
    )

    contact_email = StringVar(
        description="Email of the new Contact"
        #regex="""/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/"""
    )

    def run(self, data, commit):

        # Find site contact group if exists, create if it doesn't
        contact_group_obj_filter=ContactGroup.objects.filter(name=data['site'].tenant.name)

        if contact_group_obj_filter:
            contact_group_obj = contact_group_obj_filter[0]
            self.log_info("Found Client Contact Group: {}".format(data['site'].tenant.name))
        else:
            contact_group_obj = ContactGroup(
                name=data['site'].tenant.name,
                slug=slugify(data['site'].tenant.name)
            )
            self.log_success("Created Client Contact Group: {}".format(data['site']))
            contact_group_obj.save()


        # Find contact if it exists, create if it doesn't
        contact_obj_filter = Contact.objects.filter(name=data['contact_name'],group=contact_group_obj)

        if contact_obj_filter:
            contact_obj = contact_obj_filter[0]
            self.log_warning("Contact: {} already exists, skipping".format(data['contact_name']))
        else:
            # Add new contact
            contact_obj = Contact(
                name=data['contact_name'],
                email=data['contact_email'],
                phone=data['contact_number'],
                group=contact_group_obj,
            )

            contact_obj.save()
            self.log_success("Created Contact: {}".format(data['contact_name']))

        # Find contact assignment if it exists, create if it doesn't
        contact_assignment_obj_filter = ContactAssignment.objects.filter(contact=contact_obj, object_id=data['site'].id, content_type=18) # Content_type 58 is the site model

        if contact_assignment_obj_filter:
            contact_assignment = contact_assignment_obj_filter[0]
            self.log_warning("Contact Assignment: {} -> {} already exists, skipping".format(contact_obj.name,data['site'].name))
        else:

            contact_assignment = ContactAssignment(
                contact=contact_obj,
                object=data['site'],
                role=ContactRole.objects.get(pk=1) # Client Contact Role
            )

            contact_assignment.save()
            self.log_success("Created Contact Association: {} -> {}".format(data['contact_name'],data['site'].name))

        return "Finished"
