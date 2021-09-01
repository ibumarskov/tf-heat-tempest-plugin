from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base


class AccessControlListTest(base.FunctionalTestsBase):
    @decorators.idempotent_id('9d37bfea-0a5b-11ec-89f7-d5b7da177e1b')
    def test_template_access_control_list(self):
        template_name = 'access_control_list_heat.yaml'
        parameters = {
            'name': "AccessControlListTest",
            'display_name': "AccessControlListTest",
            'virtual_network': "tempest-fixed-net",
            'security_group': "default",
            'access_control_list_entries_acl_rule_action_list_alert': False,
        }

        self.launch_stack(template_name,
                          parameters=parameters)
        import time
        print("SLEEP 180 sec")
        time.sleep(180)
