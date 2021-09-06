from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base


class DomainTest(base.FunctionalTestsBase):

    @decorators.idempotent_id('079fc0c6-0b1f-11ec-a2d3-35b672d05c20')
    def test_template_domain(self):
        template = self.read_template('domain_heat.yaml')
        parameters = {
            'name': "DomainTest",
            'display_name': "DomainTest",
            'fq_name': "fq_name_DomainTest",
            'domain_limits_project_limit': 3,
            'domain_limits_virtual_network_limit': 10,
            'domain_limits_security_group_limit': 30,
        }
        stack_identifier = self.create_stack(template, parameters=parameters)
        stack_id = stack_identifier.split('/')[1]
        self.client.wait_for_stack_status(stack_id, 'CREATE_COMPLETE')

        # Check TungstenFabric object
        body = self.client.show_resource(stack_identifier,
                                         'template_Domain')
        uuid = body['resource'].get('physical_resource_id')
        obj = self.alarm_client.show_domain(uuid)

        self.assertEqual(obj['domain']['domain_limits']['project_limit'],
                         parameters['domain_limits_project_limit'])
        self.assertEqual(
            obj['domain']['domain_limits']['virtual_network_limit'],
            parameters['domain_limits_virtual_network_limit'])
        self.assertEqual(
            obj['domain']['domain_limits']['security_group_limit'],
            parameters['domain_limits_security_group_limit'])
