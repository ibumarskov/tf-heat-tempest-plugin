from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base


class AccessControlListTest(base.FunctionalTestsBase):
    @decorators.skip_because("Test wasn't implemented")
    @decorators.idempotent_id('9d37bfea-0a5b-11ec-89f7-d5b7da177e1b')
    def test_template_access_control_list(self):
        template = self.read_template('access_control_list_heat.yaml')
        parameters = {
            'name': "AccessControlListTest",
            'display_name': "AccessControlListTest",
            'fq_name': "fq_name_AccessControlListTest",
        }

        stack_identifier = self.create_stack(template, parameters=parameters)
        stack_id = stack_identifier.split('/')[1]
        self.client.wait_for_stack_status(stack_id, 'CREATE_COMPLETE')

        # Check TungstenFabric object
        body = self.client.show_resource(stack_identifier,
                                         'template_Domain')
        uuid = body['resource'].get('physical_resource_id')
        obj = self.access_control_client.show_domain(uuid)
