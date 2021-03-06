from tempest.lib import decorators

from tf_heat_tempest_plugin.tests.functional import base


class AlarmTest(base.FunctionalTestsBase):
    skip_check = ['fq_name', 'routing_instance', 'global_system_config',
                  'project']

    @decorators.idempotent_id('7d8914d2-0eed-11ec-9db2-892d1f23b370')
    def test_template_alarm(self):
        template = self.read_template('alarm_heat.yaml')
        resource_name = "template_Alarm"
        parameters = {
            'name': "AlarmTest",
            'display_name': "AlarmTest",
            'fq_name': "fq_name_AlarmTest",
            'alarm_severity': 0,
            'rule_operation': '!=',
            'rule_operand1':
                'NodeStatus.process_info.process_state',
            'rule_operand2_uve_attr': 'Functional',
            'rule_vars': 'process_name',
            'uve_keys': 'service-instance',
            'global_system_config': 'default-global-system-config',
            'project': self.os_admin.credentials.project_name
        }

        stack_identifier = self.create_stack(template, parameters=parameters)
        stack_id = stack_identifier.split('/')[1]
        self.client.wait_for_stack_status(stack_id, 'CREATE_COMPLETE')

        # Check TungstenFabric object
        body = self.client.show_resource(stack_identifier, resource_name)
        uuid = body['resource'].get('physical_resource_id')
        obj = self.alarm_client.show_alarm(uuid)
        self.check_tf_obj(template, resource_name, parameters,
                          obj['alarm'])
