from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base


class DomainTest(base.FunctionalTestsBase):

    @decorators.idempotent_id('079fc0c6-0b1f-11ec-a2d3-35b672d05c20')
    def test_template_access_control_list(self):
        template_name = 'domain_heat.yaml'
        parameters = {
            'name': "Domain",
            'display_name': "Domain",
            "fq_name": "simple_fq_name",
            'domain_limits_project_limit': 3,
            'domain_limits_virtual_network_limit': 10,
            'domain_limits_security_group_limit': 30,
        }
        self.launch_stack(template_name,
                          parameters=parameters)
        import time
