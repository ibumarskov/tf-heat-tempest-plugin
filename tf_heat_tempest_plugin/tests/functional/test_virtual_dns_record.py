from tempest.lib import decorators
from tempest.lib.common.utils import data_utils

from tf_heat_tempest_plugin.tests.functional import base


class VirtualDnsRecordTest(base.FunctionalTestsBase):
    skip_check = ['fq_name', 'virtual_DNS']

    @classmethod
    def resource_setup(cls):
        super(VirtualDnsRecordTest, cls).resource_setup()
        cls.dns = cls._create_virtual_dns()
        cls.addClassResourceCleanup(cls.virtual_dns_client.delete_virtual_dns,
                                    cls.dns['virtual-DNS']['uuid'])

    @classmethod
    def _create_virtual_dns(cls):
        parent_type = "domain"
        virtual_dns_data = {"domain_name": "default-domain",
                            "default_ttl_seconds": 0,
                            "record_order": "fixed"}
        display_name = data_utils.rand_name('virtual-dns')
        fq_name = ["default-domain", display_name]
        dns = cls.virtual_dns_client.create_virtual_dns(
            parent_type=parent_type,
            virtual_DNS_data=virtual_dns_data,
            display_name=display_name,
            fq_name=fq_name)
        return dns

    @decorators.idempotent_id('1c33f006-1098-11ec-91a5-753f2db7035c')
    def test_template_virtual_dns_record(self):
        template = self.read_template('virtual_DNS_record_heat.yaml')
        resource_name = "template_VirtualDnsRecord"
        parameters = {
            'name': "VirtualDnsRecordTest",
            'display_name': "VirtualDnsRecordTest",
            'fq_name': "fq_name_VirtualDnsRecordTest",
            'virtual_DNS_record_data_record_name': "mail",
            'virtual_DNS_record_data_record_type': "MX",
            'virtual_DNS_record_data_record_class': "IN",
            'virtual_DNS_record_data_record_data': "192.168.111.111",
            'virtual_DNS_record_data_record_ttl_seconds': 43200,
            'virtual_DNS_record_data_record_mx_preference': 32000,
            'virtual_DNS': self.dns['virtual-DNS']['uuid'],
        }

        stack_identifier = self.create_stack(template, parameters=parameters)
        stack_id = stack_identifier.split('/')[1]
        self.client.wait_for_stack_status(stack_id, 'CREATE_COMPLETE')

        # Check TungstenFabric object
        body = self.client.show_resource(stack_identifier,
                                         resource_name)
        uuid = body['resource'].get('physical_resource_id')
        obj = self.virtual_dns_client.show_virtual_dns_record(uuid)
        self.check_tf_obj(template, resource_name, parameters,
                          obj['virtual-DNS-record'])
