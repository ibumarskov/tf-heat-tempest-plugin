from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base


class VirtualDnsTest(base.FunctionalTestsBase):
    skip_check = ['fq_name', 'domain']

    @decorators.idempotent_id('a568ab8e-0fd3-11ec-a578-07b1c8c5404b')
    def test_template_virtual_dns(self):
        # Get default domain
        domains = self.domain_client.list_domains()
        for domain in domains['domains']:
            if 'default-domain' in domain['fq_name']:
                domain_uuid = domain['uuid']
                break

        template = self.read_template('virtual_DNS_heat.yaml')
        resource_name = "template_VirtualDns"
        parameters = {
            'name': "VirtualDnsTest",
            'display_name': "VirtualDnsTest",
            'fq_name': "fq_name_VirtualDnsTest",
            'virtual_DNS_data_domain_name': 'test.domain.net',
            'virtual_DNS_data_dynamic_records_from_client': True,
            'virtual_DNS_data_record_order': 'round-robin',
            'virtual_DNS_data_default_ttl_seconds': 43200,
            'virtual_DNS_data_next_virtual_DNS': '192.168.250.250',
            'virtual_DNS_data_floating_ip_record': 'dashed-ip-tenant-name',
            'virtual_DNS_data_external_visible': False,
            'virtual_DNS_data_reverse_resolution': False,
            'domain': domain_uuid,
        }

        stack_identifier = self.create_stack(template, parameters=parameters)
        stack_id = stack_identifier.split('/')[1]
        self.client.wait_for_stack_status(stack_id, 'CREATE_COMPLETE')

        # Check TungstenFabric object
        body = self.client.show_resource(stack_identifier, resource_name)
        uuid = body['resource'].get('physical_resource_id')
        obj = self.virtual_dns_client.show_virtual_dns(uuid)
        self.check_tf_obj(template, resource_name, parameters,
                          obj['virtual-DNS'])
